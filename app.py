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
    return redirect(url_for('complete_user', message="Bienvenue! Allez, encore un effort :)"))


#Quand le user a répondu au questionnaire
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

    return redirect(url_for('programs', iduser=user_id))
     

#Liste des programmes disponibles
@app.route('/users/<int:iduser>/programs')
def programs(iduser):
    mycursor = mydb.cursor(dictionary=True)
    mycursor.execute("SELECT id_program, name, description FROM programs")
    programs = mycursor.fetchall()
    mycursor.close()
    return render_template('programmes.html', programs=programs, iduser=iduser)


#Connecte le user avec le programme (table de jonction)
@app.route('/users/<int:iduser>/assign/<int:id_program>')
def assign_program(iduser, id_program):
        mycursor = mydb.cursor()
        # Insérez les données dans votre table de jointure
        mycursor.execute("INSERT INTO users_programs (iduser, id_program) VALUES (%s, %s)", (iduser, id_program))
        mydb.commit()
        mycursor.close()
        return redirect(url_for('get_user', iduser=iduser))

@app.route('/users/questions')
def complete_user():
    return render_template('questions.html', message = request.args.get('message'))
     

#Affiche l'utilisateur et ses propriétés (programme et exercices)
@app.route('/users/<iduser>')
def get_user(iduser):
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
                    return render_template('user.html', user=user, program=program, progress = progress, exercises = exercises)
            else:
                return render_template('error.html', message="Aucun programme assigné à cet utilisateur.")
        else:
            return render_template('error.html', message="Utilisateur non trouvé.")
    


#Page pour modifier les données du user
@app.route('/users/<iduser>/edit', methods=['GET', 'POST'])
def edit_user(iduser):
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

    


def calculate_progress(user_id):
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


if __name__ == "__main__":
    app.run(debug=True)
