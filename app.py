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
     
     return redirect(url_for('get_user', username=username))

@app.route('/users/<username>')
def get_user(username):
     mycursor = mydb.cursor()
     query = 'SELECT * FROM users WHERE username=%s'
     mycursor.execute(query, (username,))
     user = mycursor.fetchone()
     mycursor.close()
    
     if user:
        return render_template('user.html', username=user[1])
     else:
        return jsonify({"error": "Utilisateur non trouvé"}), 404

if __name__ == "__main__":
    app.run(debug=True)
