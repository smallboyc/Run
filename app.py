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
     



#Programmes
@app.route('/select_program')
def select_program():
    mycursor = mydb.cursor()
    mycursor.execute("SELECT idprogram, name_program FROM program")
    programs = mycursor.fetchall()
    mycursor.close()
    return render_template('select_program.html', programs=programs)

@app.route('/add_program_to_user', methods=['POST'])
def add_program_to_user():
    program_id = request.form['program_id']
    return redirect(url_for('select_exercise', program_id=program_id))



#Sélectionner les exercices d'un programme
@app.route('/select_exercise/<int:program_id>')
def select_exercise(program_id):
    mycursor = mydb.cursor()
    mycursor.execute("SELECT idexercises, name FROM exercises")
    exercises = mycursor.fetchall()
    mycursor.close()
    return render_template('select_exercise.html', exercises=exercises, program_id=program_id)






if __name__ == "__main__":
    app.run(debug=True)
