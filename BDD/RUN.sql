CREATE TABLE users (
  iduser INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  firstname VARCHAR(45) NULL,
  surname VARCHAR(45) NULL,
  email VARCHAR(45) NULL,
  password_hash VARCHAR(60) NULL,
  weight FLOAT NULL,
  height FLOAT NULL,
  animal VARCHAR(45) NULL
);

CREATE TABLE exercises (
    id_exercise INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    time INT,
    distance INT,
    target_desc TEXT,
    target_result INT,
    completed BOOLEAN
);

CREATE TABLE programs (
    id_program INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    completed BOOLEAN
);

CREATE TABLE users_programs (
    iduser INT,
    id_program INT,
    PRIMARY KEY (iduser, id_program),
    FOREIGN KEY (iduser) REFERENCES users(iduser),
    FOREIGN KEY (id_program) REFERENCES programs(id_program)
);

CREATE TABLE exercises_programs (
    id_exercise INT,
    id_program INT,
    PRIMARY KEY (id_exercise, id_program),
    FOREIGN KEY (id_exercise) REFERENCES exercises(id_exercise),
    FOREIGN KEY (id_program) REFERENCES programs(id_program)
);

INSERT INTO exercises (name, description, time, distance, target_desc, target_result, completed) VALUES 
('Guépard', 'Courir après un inconnu le plus longtemps possible', 0, 0, 'inconnus effrayés', 0, false),
('Taureau', 'Cours après chaque personne habillée en rouge que tu croises le plus de fois possible', 0, 0, 'nombre de personnes poursuivies', 0, false),
('Loup', 'Courir le plus loin possible en meute avec tes potes', 0, 0, 'nombre de potes', 0, false);

INSERT INTO programs (name, description, completed) VALUES 
('VITESSE', 'Aussi rapide que Leclerc', false),
('PUISSANCE', 'Aussi fort que The Rock', false),
('ENDURANCE', 'Je sais pas', false);

INSERT INTO exercises_programs (id_exercise, id_program) VALUES 
(1, 1),
(2, 2),
(3, 3);

