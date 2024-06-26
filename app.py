from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
import mysql.connector

import config

app = Flask(__name__)

mydb = mysql.connector.connect(
    host=config.Config.DB_HOST,
    user=config.Config.DB_USER,
    password=config.Config.DB_PASSWORD,
    database=config.Config.DB_NAME
)

# Accueil
@app.route('/')
def root():
    return render_template('index.html')

# Enregistrement
@app.route('/register')
def register():
    return render_template('register.html')

# User essaye de créer son compte
@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    firstname = request.form["firstname"]
    surname = request.form["surname"]
    password_hash = request.form["password_hash"]
    email = request.form["email"]

    mycursor = mydb.cursor()

     # Vérification si l'email existe déjà
    mycursor.execute("SELECT * FROM users WHERE email=%s", (email,))
    existing_user = mycursor.fetchone()
    print(f"Vérification de l'email : {existing_user}")

    if existing_user:
        print('Email existant')
        return render_template('error.html', message="L'email existe déjà")
    
    # Insertion de l'utilisateur si l'email n'existe pas
    query = "INSERT INTO users (firstname, surname, email, password_hash) VALUES (%s, %s, %s, %s)"
    val = (firstname, surname, email, password_hash)
    mycursor.execute(query, val)
    mydb.commit()
    mycursor.close()
    print("Utilisateur inséré avec succès")
    return redirect(url_for('complete_user'))
    
        



@app.route('/users/questions')
def complete_user():
    return render_template('questions.html')

@app.route('/users/firstname', methods=['POST'])
def questions():
    weight = request.form["weight"]
    height = request.form["height"]
    animal = request.form["animal"]
    mycursor = mydb.cursor()
    try:
        query = "INSERT INTO user_details (weight, height, animal) VALUES (%s, %s, %s)"
        val = (weight, height, animal)
        mycursor.execute(query, val)
        mydb.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        mydb.rollback()
    finally:
        mycursor.close()

    return redirect(url_for('get_user', iduser=iduser))

@app.route('/users/<iduser>')
def get_user(iduser):
     mycursor = mydb.cursor()
     query = 'SELECT * FROM users WHERE iduser=%s'
     mycursor.execute(query, (iduser,))
     user = mycursor.fetchone()
     mycursor.close()
    
     if user:
        return render_template('user.html', iduser=user[0])
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
