from flask import Flask, render_template, request, redirect

app = Flask(__name__)

@app.route("/")
def hello_world():
     return render_template("Home.html")

@app.route("/")
def programmes():
     return render_template("programmes.html")