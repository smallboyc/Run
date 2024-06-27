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
        mycursor.execute('SELECT firstname, surname, email FROM users WHERE iduser=%s', (iduser,))
        user = mycursor.fetchone()
        
        if user:
            # Récupérer le programme assigné à l'utilisateur depuis la table de jointure
            mycursor.execute("SELECT p.name, p.id_program FROM programs p JOIN users_programs up ON p.id_program=up.id_program JOIN users u ON up.iduser=u.iduser WHERE u.iduser=%s AND p.completed = FALSE",(iduser,))
            program = mycursor.fetchone()
            
            if program:
                 progress = calculate_progress(iduser)
                 program_id = program['id_program']

                #Sélectionne tous les exercices
                 mycursor.execute("SELECT e.id_exercise, e.name, e.description FROM exercises e JOIN exercises_programs ep ON e.id_exercise = ep.id_exercise WHERE ep.id_program = %s ORDER BY e.id_exercise", (program_id,))
                 exercises = mycursor.fetchall()

                #Sélectionne les exercices qui ne sont pas complétés
                 mycursor.execute("SELECT e.id_exercise, e.name, e.description, e.completed FROM exercises e JOIN exercises_programs ep ON e.id_exercise = ep.id_exercise WHERE ep.id_program = %s AND e.completed = FALSE ORDER BY e.id_exercise", (program_id,))
                 next_exercise = mycursor.fetchone()

                 mycursor.close()

                 return render_template('user.html', user=user, program=program, progress = progress, exercises=exercises, next_exercise=next_exercise)
            else:
                mycursor.close()
                return render_template('error.html', message="Aucun programme assigné à cet utilisateur.")
        else:
            mycursor.close()
            return render_template('error.html', message="Utilisateur non trouvé.")
    



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
        mycursor.execute("INSERT INTO users_programs (iduser, id_program) VALUES (%s, %s)", (iduser, id_program))
        mydb.commit()
        mycursor.close()
        return redirect(url_for('get_user', iduser=iduser))


@app.route('/users/show_exercise/<int:id_exercice>')
def show_exercise(id_exercise):

    mycursor = mydb.cursor(dictionary=True)

    #Sélectionne l'exercice avec le bon id'
    mycursor.execute("SELECT name, description, target_desc FROM exercises WHERE id_exercise=%s", (id_exercise,))
    selected_exercise = mycursor.fetchone()

    mycursor.close()

    return render_template('exercices.html', selected_exercise=selected_exercise)


@app.route('/next_exercise/<int:id_exercise>', methods=['POST'])
def next_exercise(id_exercise):
    user_id = session.get('user_id')

    mycursor = mydb.cursor()

    #Mise à jour de l'exercice
    mycursor.execute("UPDATE exercises SET completed = TRUE WHERE id_exercise = %s" , (id_exercise,))

    #Nombre d'exercices pas complétés restants
    mycursor.execute("SELECT COUNT(*) as remaining FROM exercises e JOIN exercises_programs ep ON e.id_exercise = ep.id_exercise WHERE ep.id_program = (SELECT id_program FROM users_programs WHERE iduser = %s) AND e.completed = FALSE", (user_id,))
    remaining_exercises = mycursor.fetchone()

    #Mise à jour de l'état completed de la table program si tous les exercices sont finis
    if remaining_exercises['remaining'] == 0:
        mycursor.execute("UPDATE programs SET completed = TRUE WHERE id_program = (SELECT id_program FROM users_programs WHERE iduser = %s)", (user_id,))

    #Sélectionne l'exercice d'après
    mycursor.execute("SELECT e.id_exercise FROM exercises e JOIN exercises_programs ep ON e.id_exercise = ep.id_exercise WHERE ep.id_program = (SELECT id_program FROM users_programs WHERE iduser = %s) AND e.completed = FALSE ORDER BY e.id_exercise LIMIT 1", (user_id,))
    next_exercise = mycursor.fetchone()

    mydb.commit()
    mycursor.close() 

    #Vérifie si il reste des exercices à faire
    if next_exercise:
        return redirect(url_for('show_exercise', id_exercise=next_exercise['id_exercise']))
    else:
        return redirect(url_for('get_user', iduser=user_id))

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
