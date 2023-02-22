import flask
from flask import Flask, request, redirect

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
	return redirect('login.html', error=error)



@app.route("/canvas")
def get_canvas():
	# retrieve entire canvas
	pass


@app.route("/canvas/<int:pixel_id>")
def update_pixel(pixel_id, rgb):
	# update pixel to new rgb value
    change_pixel(pixel_id, rgb)
    

@app.route("/<int: user_id>/countdown")
def get_countdown(user_id):
	# get countdown left for user
    retrieve_countdown(user_id)

