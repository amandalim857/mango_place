import flask
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



@app.route("/canvas")
def get_canvas():
	# retrieve entire canvas
	pass


@app.route("/canvas/<int:x>/<int:y>")
def update_pixel(pixel_id, rgb):
	# update pixel to new rgb value
    change_pixel(pixel_id, rgb)
    

@app.route("/user/<int:user_id>/countdown")
# prefixed w user to know it is from a user
def get_countdown(user_id):
	# get countdown left for user
    retrieve_countdown(user_id)

