import flask
from flask import Flask, request, redirect, url_for
from db import *

app = Flask(__name__)

@app.route("/")
def index():
	return flask.render_template("index.html")


@app.route('/logout')
def logout():
    logout_user()

@app.route("/login", methods=['POST','GET'])
def login():
	error = None
	if request.method == 'POST':
		username = request.form["username"]
		password = request.form["password"]
		if valid_login(username, password):
			return login_user(username)
		else:
			error = 'Invalid username/password'
	return redirect(url_for('login'), error=error)



@app.route("/canvas")
def get_canvas():
	# retrieve entire canvas
	pass


@app.route("/canvas/<int:x>/<int:y>")
def update_pixel(pixel_id, rgb):
	# update pixel to new rgb value
    change_pixel(pixel_id, rgb)
    

@app.route("/user/<int: user_id>/countdown")
# prefixed w user to know it is from a user
def get_countdown(user_id):
	# get countdown left for user
    retrieve_countdown(user_id)

