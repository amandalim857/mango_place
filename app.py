from flask import Flask, request, redirect, url_for, render_template, session, Response, flash
from config import SECRET_KEY
from db import *

app = Flask(__name__)
app.secret_key = SECRET_KEY

@app.route("/")
def index():
	if "username" in session:
		return render_template('canvas.html')
	else:
		redirect(url_for('login'))

# Login/ Logout
@app.route('/logout')
def logout():
	session.pop('username', None)
	return redirect(url_for("login"))

@app.route("/login", methods=['POST','GET'])
def login():
	error = None
	users = UserTable()
	if request.method == 'POST':
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

# Canvas
@app.route("/canvas", methods=['GET'])
def get_canvas():
	canvas = CanvasTable()
	if not canvas.canvas_exists():
		canvas.create_canvas_table()
	img_file = canvas.get_canvas_table()
	img = img_file.getvalue()
	return Response(response=img, mimetype='image/png')

# Pixel Data
@app.route("/canvas/<int:row>/<int:col>", methods=['PUT'])
def place_pixel(row, col):
	hexcolor = request.args.get('hexcolor')
	# username = session["username"]
	username = "megan"
	red, green, blue = bytes.fromhex(hexcolor)
	rgb = [red, green, blue]
	canvas, pixel_table, countdown_table = CanvasTable(), PixelTable(), CountdownTable()
	timestamp = datetime.datetime.utcnow()
	time_waited = countdown_table.seconds_waited(username)

	if time_waited >= 300:
		canvas.update_canvas(row, col, rgb)
		pixel_table.upsert_pixel_data(row, col, username, rgb, timestamp)
		countdown_table.upsert_user_timestamp(username, timestamp)
		flash(f'Inserted {row}, {col}')
	else:
		min_left = (300 - time_waited) // 60
		flash(f'You have to wait {min_left} min more before placing your next tile!')


users, canvas, pixel_table, countdown_table = UserTable(), CanvasTable(), PixelTable(), CountdownTable()
users.create_users_table()
if not canvas.canvas_exists():
	canvas.create_canvas_table() 
pixel_table.create_pixel_table()
countdown_table.create_countdown_table()
