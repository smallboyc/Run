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

def is_logged_in():
    return 'user_id' in session

def is_authorized(iduser):
    return is_logged_in() and session['user_id'] == iduser

# Accueil
@app.route('/')
def root():
    return render_template('index.html')


#Affichage de la page Register
@app.route('/register')
def register():
    return render_template('register.html', message = request.args.get('message'))

#Affichage de la page Log in
@app.route('/login')
def login():
    return render_template('login.html')

#On détermine si le user se log correctement.
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
        return redirect(url_for('register', message="Connexion impossible. Enregistrez-vous !"))

        
#On détermine si le user s'est enregistré correctement, si oui -> questionnaire
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
    return redirect(url_for('complete_user', message="Bienvenue! Allez, encore un effort :)", iduser = user_id))

@app.route('/users/<int:iduser>/questions')
def complete_user(iduser):
    if not is_authorized(iduser):
            return redirect(url_for('complete_user', iduser = session['user_id']))
    return render_template('questions.html', message = request.args.get('message'), iduser = iduser)

#Quand le user a répondu au questionnaire
@app.route('/users/<int:iduser>/questionnaire', methods=['POST'])
def questions(iduser):
    if not is_authorized(iduser):
            return redirect(url_for('questions', iduser = session['user_id']))
    
    weight = request.form["weight"]
    height = request.form["height"]
    animal = request.form["animal"]

    
    mycursor = mydb.cursor()
    sql = "UPDATE users SET weight=%s, height=%s, animal=%s WHERE iduser=%s"
    val = (weight, height, animal, iduser) 

    mycursor.execute(sql, val)
    mydb.commit()
    mycursor.close()

    return redirect(url_for('programs', iduser=iduser))
     

#Liste des programmes disponibles
@app.route('/users/<int:iduser>/programs')
def programs(iduser):
    if not is_authorized(iduser):
            return redirect(url_for('programs', iduser = session['user_id']))
    
    mycursor = mydb.cursor(dictionary=True)
    mycursor.execute("SELECT id_program, name, description FROM programs")
    programs = mycursor.fetchall()
    mycursor.close()
    return render_template('programmes.html', programs=programs, iduser=iduser)


#Connecte le user avec le programme (table de jonction)
@app.route('/users/<int:iduser>/assign/<int:id_program>')
def assign_program(iduser, id_program):
        if not is_authorized(iduser):
            return redirect(url_for('programs', iduser = session['user_id']))
         
        mycursor = mydb.cursor(dictionary=True)

        # Récupérer le premier exercice du programme
        mycursor.execute("SELECT e.id_exercise FROM exercises e JOIN exercises_programs ep ON e.id_exercise = ep.id_exercise WHERE ep.id_program = %s ORDER BY e.id_exercise ASC LIMIT 1" , (id_program,))
        first_exercise = mycursor.fetchone()
    
        if first_exercise:
            first_exercise_id = first_exercise['id_exercise']
        else:
            first_exercise_id = None

        # Insérez les données dans votre table de jointure
        mycursor.execute("INSERT INTO users_programs (iduser, id_program, current_exercise_id) VALUES (%s, %s, %s)", (iduser, id_program,first_exercise_id))
        mydb.commit()
    
        mycursor.close()
        return redirect(url_for('get_user', iduser=iduser))


#Affiche l'utilisateur et ses propriétés (programme et exercices)
@app.route('/users/<int:iduser>')
def get_user(iduser):
    if not is_authorized(iduser):
        return redirect(url_for('get_user', iduser = session['user_id']))

    mycursor = mydb.cursor(dictionary=True)
    mycursor.execute('SELECT iduser, firstname, surname, email FROM users WHERE iduser=%s', (iduser,))
    user = mycursor.fetchone()

    if user:
        # Récupérer le programme assigné à l'utilisateur depuis la table de jointure
        mycursor.execute("SELECT p.name, p.id_program FROM programs p JOIN users_programs up ON p.id_program=up.id_program JOIN users u ON up.iduser=u.iduser WHERE u.iduser=%s",(iduser,))
        program = mycursor.fetchone()

        if program:
            progress = calculate_progress(iduser)
            program_id = program['id_program']
            mycursor.execute("SELECT exercises.name, exercises.description FROM exercises JOIN exercises_programs ON exercises.id_exercise=exercises_programs.id_exercise JOIN programs ON exercises_programs.id_program=programs.id_program WHERE programs.id_program=%s LIMIT 5", (program_id,))
            exercises = mycursor.fetchall()
            mycursor.close()
            if exercises:
                changed_weight = calculate_weight(iduser)
                return render_template('user.html', user=user, program=program, progress = progress, changed_weight = changed_weight, exercises = exercises)
            else:
                return render_template('error.html', message="Aucun programme assigné à cet utilisateur.")
        else:
            return render_template('error.html', message="Utilisateur non trouvé.")
    


#Page pour modifier les données du user
@app.route('/users/<int:iduser>/edit', methods=['GET', 'POST'])
def edit_user(iduser):
    if not is_authorized(iduser):
        return redirect(url_for('edit_user', iduser = session['user_id']))
    
    mycursor = mydb.cursor(dictionary=True)
    
    if request.method == 'GET':
        # Récupérer les informations de l'utilisateur
        mycursor.execute('SELECT iduser, firstname, surname, email FROM users WHERE iduser=%s', (iduser,))
        user = mycursor.fetchone()
        # Récupérer l'id du programme du user 
        mycursor.execute('SELECT * FROM programs JOIN users_programs ON programs.id_program=users_programs.id_program WHERE iduser=%s', (iduser,))
        user_program = mycursor.fetchone()
        # Récupère tous les programmes
        mycursor.execute('SELECT * FROM programs')
        programs = mycursor.fetchall()
        mycursor.close()

        # Affiche les données actuelles du user
        return render_template('edit_user.html', user=user, programs=programs, user_program=user_program, iduser=iduser)

    elif request.method == 'POST':
        # Récupérer les données du formulaire
        firstname = request.form['firstname']
        surname = request.form['surname']
        email = request.form['email']
        id_program = request.form['id_program']

        # Mettre à jour les informations du user
        mycursor.execute("UPDATE users SET firstname=%s, surname=%s, email=%s WHERE iduser=%s", (firstname, surname, email, iduser))
        # Mettre à jour le programme du user
        mycursor.execute("UPDATE users_programs SET id_program=%s WHERE iduser=%s", (id_program, iduser))
        
        mydb.commit()
        mycursor.close()
        return redirect(url_for('get_user', iduser=iduser))

    
#Affiche l'exercice actuel
@app.route('/users/<int:iduser>/current_exercise')
def current_exercise(iduser):
    if not is_authorized(iduser):
        return redirect(url_for('login'))

    mycursor = mydb.cursor(dictionary=True)
    mycursor.execute('''
        SELECT *
        FROM exercises e 
        JOIN users_programs up ON e.id_exercise = up.current_exercise_id 
        WHERE up.iduser = %s
    ''', (iduser,))
    exercise = mycursor.fetchone()

    if exercise:
        return render_template('exercise.html', exercise=exercise, iduser=iduser)
        # return jsonify(exercise)
    else:
        return render_template('error.html', message="Aucun exercice disponible.", iduser=iduser)



#Met à jour l'exercice et passe au suivant
@app.route('/users/<int:iduser>/complete_exercise', methods=['POST'])
def complete_exercise(iduser):
    if not is_authorized(iduser):
        return redirect(url_for('login'))

    exercise_id = request.form['exercise_id']
    mycursor = mydb.cursor(dictionary=True)
    mycursor.execute('UPDATE exercises SET completed = TRUE WHERE id_exercise = %s', (exercise_id,))
    
    # Récupérer le prochain exercice
    mycursor.execute('''
        SELECT e.id_exercise
        FROM exercises e
        JOIN exercises_programs ep ON e.id_exercise = ep.id_exercise
        JOIN users_programs up ON ep.id_program = up.id_program
        WHERE up.iduser = %s AND e.id_exercise > %s
        ORDER BY e.id_exercise ASC
        LIMIT 1
    ''', (iduser, exercise_id))
    next_exercise = mycursor.fetchone()

    if next_exercise:
        next_exercise_id = next_exercise['id_exercise']
    else:
        next_exercise_id = None

    # Mettre à jour le current_exercise_id pour l'utilisateur
    mycursor.execute('UPDATE users_programs SET current_exercise_id = %s WHERE iduser = %s', (next_exercise_id, iduser))
    
    mydb.commit()
    mycursor.close()

    return redirect(url_for('get_user', iduser=iduser))


#Affichage l'exercice en cours

def calculate_progress(user_id):
    if not is_authorized(user_id):
        return redirect(url_for('login'))
    
    mycursor = mydb.cursor(dictionary=True)
    
    # Nombre total d'exercices dans le programme de l'utilisateur
    mycursor.execute("SELECT COUNT(*) as total_exercises FROM exercises e JOIN exercises_programs ep ON e.id_exercise = ep.id_exercise JOIN programs p ON ep.id_program = p.id_program JOIN users_programs up ON p.id_program = up.id_program WHERE up.iduser = %s", (user_id,))
    total_exercises = mycursor.fetchone()['total_exercises']
    
    # Nombre d'exercices complétés
    mycursor.execute("SELECT COUNT(*) as completed_exercises FROM exercises e JOIN exercises_programs ep ON e.id_exercise = ep.id_exercise JOIN programs p ON ep.id_program = p.id_program JOIN users_programs up ON p.id_program = up.id_program WHERE up.iduser = %s AND e.completed = TRUE", (user_id,))
    completed_exercises = mycursor.fetchone()['completed_exercises']
    
    mycursor.close()
    
    if total_exercises == 0:
        return 0
    
    progress_percentage = (completed_exercises / total_exercises) * 100
    return progress_percentage


def calculate_weight(user_id):

    mycursor = mydb.cursor(dictionary=True)

    mycursor.execute("SELECT weight FROM users WHERE iduser=%s", (user_id,))
    weight = mycursor.fetchone()['weight']

    mycursor.execute("SELECT e.time, e.distance, e.target_result FROM exercises e JOIN exercises_programs ep ON e.id_exercise = ep.id_exercise JOIN programs p ON ep.id_program = p.id_program JOIN users_programs up ON p.id_program = up.id_program WHERE iduser=%s AND e.completed = TRUE", (user_id,))
    data_completed_exercise = mycursor.fetchall()

    mycursor.close()

    all_data = 0

    for exercise in data_completed_exercise:
        all_data = int(exercise['time']) + int(exercise['distance']) + int(exercise['target_result'])
    
    changed_weight = all_data

    return changed_weight




if __name__ == "__main__":
    app.run(debug=True)
