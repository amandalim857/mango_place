from flask import Flask, request, redirect, url_for, render_template, session, Response, make_response
from functools import wraps
from config import SECRET_KEY
from db import *
import helper

def create_app(database_path='schema.db'):
	app = Flask(__name__)
	app.secret_key = SECRET_KEY

	def logged_in(f):
		@wraps(f)
		def decorated_function(*args, **kwargs):
			if session.get('username') is not None:
				return f(*args, **kwargs)
			else:
				return make_response('you must be logged in to carry out this function', 401)
		return decorated_function


	@app.route('/')
	def index():
		return render_template('index.html', authenticated='username' in session)

	# Login/ Logout
	@app.route('/signup', methods=['POST'])
	def signup():
		users = UserTable(database_path)
		username = request.form.get('username')
		password = request.form.get('password')
		if username is None or password is None:
			return make_response('username or password was not input', 400)
		if users.valid_username(username):
			return redirect(url_for('index', error='account_exists'))

		users.add_user(username, password)

		return redirect(url_for('index'))

	@app.route('/login', methods=['POST'])
	def login():
		error = None

		users = UserTable(database_path)
		username = request.form.get('username')
		password = request.form.get('password')
		if username is None or password is None:
			return make_response('username or password was not input', 400)
		if users.valid_username(username):
			if users.valid_login(username, password):
				session['username'] = username
			else:
				error = 'incorrect_password'
		else:
			error = 'nonexistent_username'

		return redirect(url_for('index', error=error))

	@app.route('/logout')
	@logged_in
	def logout():
		session.pop('username', None)
		return redirect(url_for('login'))

	# Canvas
	@app.route('/canvas')
	def get_canvas():
		canvas = CanvasTable(database_path)
		if not canvas.canvas_exists():
			canvas.create_canvas_table()
		img_file = canvas.get_canvas_table()
		img = img_file.getvalue()
		return Response(response=img, mimetype='image/png')
	
	# Pixel Data
	@app.route('/canvas/<int:row>/<int:col>', methods=['PUT'])
	@logged_in
	def place_pixel(row, col):
		hexcolor = request.args.get('hexcolor')
		username = session.get('username')
		if hexcolor[0] != "#":
			return make_response('rgb code require # in front', 400)
		colors = bytes.fromhex(hexcolor[1:])
		if len(colors) != 3:
			return make_response('the hex must contain exactly 3 colors', 400)
		rgb = [color for color in colors]
		canvas, pixel_table, countdown_table = CanvasTable(database_path), PixelTable(database_path), CountdownTable(database_path)			
		timestamp = helper.helper_datetime_utcnow()
		time_waited = countdown_table.seconds_waited(username)
		if time_waited >= 300:
			canvas.update_canvas_pixel(row, col, rgb)
			pixel_table.upsert_pixel_data(row, col, username, rgb, timestamp)
			countdown_table.upsert_user_timestamp(username, timestamp)
			return Response()

		seconds_left = (300 - time_waited)
		response = make_response(f'You have to wait {seconds_left} seconds more before placing your next tile!', 429)
		response.mimetype = 'text/plain'
		response.headers['Retry-After'] = seconds_left
		return response

	users, canvas, pixel_table, countdown_table = UserTable(database_path), CanvasTable(database_path), PixelTable(database_path), CountdownTable(database_path)
	users.create_users_table()
	if not canvas.canvas_exists():
		canvas.create_canvas_table()
	pixel_table.create_pixel_table()
	countdown_table.create_countdown_table()

	return app
