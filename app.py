from flask import Flask, render_template, jsonify, request, redirect, url_for
import mysql.connector

import config

app = Flask(__name__)

mydb = mysql.connector.connect(
     host=config.Config.DB_HOST,
     user=config.Config.DB_USER,
     password=config.Config.DB_PASSWORD,
     database=config.Config.DB_NAME
)

@app.route('/')
def root():
    return render_template('index.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/add_user', methods=['POST'])
def add_user():
     username = request.form["username"]
     password_hash = request.form["password_hash"]
     email = request.form["email"]
     mycursor = mydb.cursor()
     try:
          sql = "INSERT INTO users (iduser, username, password_hash, email) VALUES (%s, %s, %s, %s)"
          val = (0, username, password_hash, email)
          mycursor.execute(sql, val)
          mydb.commit()
     except mysql.connector.Error as err:
          print(f"Error: {err}")
          mydb.rollback()
     finally:
          mycursor.close()
     
     return redirect(url_for('/users/', username=username))

@app.route('/users<username>')
def get_users(username):
     mycursor = mydb.cursor()
     query = f'SELECT * FROM users WHERE username={username}'
     mycursor.execute(query)
     user = mycursor.fetchone()
     mycursor.close()
    
     if user:
        return jsonify(user)
     else:
        return jsonify({"error": "User not found"}), 404


if __name__ == "__main__":
    app.run(debug=True)
