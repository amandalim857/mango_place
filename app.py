from flask import Flask, request, redirect, url_for, render_template, session
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
	if request.method == 'POST':
		username = request.form["username"]
		password = request.form["password"]
		if valid_username(username):
			if valid_login(username, password):
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
	if not canvas.check_canvas_exists():
		canvas.create_canvas_table()
	return canvas.get_canvas_table()

@app.route("/canvas/<int:row>/<int:col>")
def update_pixel(row, col, userid, rgb, timestamp):
	canvas = CanvasTable()
	canvas.update_canvas(row, col, rgb)

@app.route("/user/<int:user_id>/countdown")
# prefixed w user to know it is from a user
def get_countdown(user_id):
	# get countdown left for user
    retrieve_countdown(user_id)
