from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, session
import mysql.connector
import bcrypt
import config



app = Flask(__name__)
app.secret_key = config.Config.secret_key


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


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/login_user', methods =['POST'])
def login_user():
    mycursor = mydb.cursor(dictionary=True)
    email = request.form["email"]
    password = request.form["password"]

    mycursor.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = mycursor.fetchone()

    if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
        session['user_id'] = user['iduser']
        session['user_email'] = user['email']
        return redirect(url_for('get_user', iduser=user['iduser']))
    else:
        return redirect(url_for('register'))

        

@app.route('/register_user', methods=['GET', 'POST'])
def register_user():
    firstname = request.form["firstname"]
    surname = request.form["surname"]
    password = request.form["password"]
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
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    query = "INSERT INTO users (firstname, surname, email, password_hash) VALUES (%s, %s, %s, %s)"
    val = (firstname, surname, email, password_hash)
    mycursor.execute(query, val)
    mydb.commit()
    user_id = mycursor.lastrowid 
    session['user_id'] = user_id
    mycursor.close()
    print("Utilisateur inséré avec succès")
    return redirect(url_for('complete_user'))


@app.route('/users/questions')
def complete_user():
    return render_template('questions.html')


@app.route('/users/<iduser>')
def get_user(iduser):
     mycursor = mydb.cursor(dictionary=True)
     mycursor.execute('SELECT firstname, surname, email FROM users WHERE iduser=%s',(iduser,))
     user = mycursor.fetchone()
     mycursor.close()
     if user: #affiche la page de l'utilisateur
        return render_template('user.html', user=user)
     else:
        return render_template('error.html', message="Erreur")
     


@app.route('/users/questionnaire', methods=['POST'])
def questions():
    weight = request.form["weight"]
    height = request.form["height"]
    animal = request.form["animal"]

    user_id = session.get('user_id')
    
    mycursor = mydb.cursor()
    sql = "UPDATE users SET weight=%s, height=%s, animal=%s WHERE iduser=%s"
    val = (weight, height, animal, user_id) 

    mycursor.execute(sql, val)
    mydb.commit()
    mycursor.close()

    return redirect(url_for('get_user', iduser=user_id))


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
