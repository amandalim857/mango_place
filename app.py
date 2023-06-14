from flask import Flask, request, redirect, url_for, render_template, session, Response, make_response
from config import SECRET_KEY
from db import *

app = Flask(__name__)
app.secret_key = SECRET_KEY

@app.route("/")
def index():
	if "username" in session:
		return render_template('canvas.html')
	else:
		redirect(url_for("login"))

# Login/ Logout
@app.route("/signup", methods=['POST','GET'])
def signup():
	users = UserTable()
	if request.method == 'POST':
		username = request.form["username"]
		password = request.form["password"]
		if users.valid_username(username):
			return redirect(url_for("index"), error="account_exists")
		users.add_user(username, password)
		return redirect(url_for("index"))

@app.route("/login", methods=['POST','GET'])
def login():
	error = None
	users = UserTable()
	if request.method == 'POST':
		if username not in request or password not in request:
			flash("Username or password missing") # TODO
		username = request.form["username"]
		password = request.form["password"]
		if users.valid_username(username):
			if users.valid_login(username, password):
				session['username'] = username
				return render_template('canvas.html')
			error = 'Incorrect password'
		else:
			error = 'Username does not exist'
		return render_template('login.html', error=error)

@app.route('/logout')
def logout():
	session.pop('username', None)
	return redirect(url_for("login"))


# Canvas
@app.route("/canvas")
def get_canvas():
	canvas = CanvasTable(database_path)
	if not canvas.canvas_exists():
		canvas.create_canvas_table()
	img_file = canvas.get_canvas_table()
	img = img_file.getvalue()
	return Response(response=img, mimetype='image/png')

# Pixel Data
@app.route("/canvas/<int:row>/<int:col>", methods=['PUT'])
def place_pixel(row, col):
	hexcolor = request.args.get('hexcolor')
	try:
		username = session["username"]
	except KeyError:
		response = make_response("You need to be logged in to add a pixel", 401)
		response.headers['WWW-Authenticate'] = 'Basic realm="Login required"'
		return response
	red, green, blue = bytes.fromhex(hexcolor[1:])
	rgb = [red, green, blue]
	canvas, pixel_table, countdown_table = CanvasTable(database_path), PixelTable(database_path), CountdownTable(database_path)			
	timestamp = helper.helper_datetime_utcnow()
	time_waited = countdown_table.seconds_waited(username)
	if time_waited >= 300:
		canvas.update_canvas_pixel(row, col, rgb)
		pixel_table.upsert_pixel_data(row, col, username, rgb, timestamp)
		countdown_table.upsert_user_timestamp(username, timestamp)
		return Response()

	if time_waited >= 300:
		canvas.update_canvas(row, col, rgb)
		pixel_table.upsert_pixel_data(row, col, username, rgb, timestamp)
		countdown_table.upsert_user_timestamp(username, timestamp)
	else:
		seconds_left = (300 - time_waited)
		response = make_response(f"You have to wait {seconds_left} seconds more before placing your next tile!", 429)
		response.mimetype = "text/plain"
		response.headers["Retry-After"] = seconds_left
		return response

users, canvas, pixel_table, countdown_table = UserTable(), CanvasTable(), PixelTable(), CountdownTable()
users.create_users_table()
if not canvas.canvas_exists():
	canvas.create_canvas_table() 
pixel_table.create_pixel_table()
countdown_table.create_countdown_table()
