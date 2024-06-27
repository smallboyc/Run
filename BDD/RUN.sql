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
    id_exercise INT PRIMARY KEY,
    name VARCHAR(100),
    description TEXT
);

CREATE TABLE programs (
    id_program INT PRIMARY KEY,
    name VARCHAR(100),
    description TEXT
);


CREATE TABLE users_programs (
    iduser INT,
    id_program INT,
    PRIMARY KEY (iduser, id_program),
    FOREIGN KEY (iduser) REFERENCES users(iduser),
    FOREIGN KEY (id_program) REFERENCES programmes(id_program)
);

CREATE TABLE exercises_programs (
    id_exercise INT,
    id_program INT,
    PRIMARY KEY (id_exercise, id_program),
    FOREIGN KEY (id_exercise) REFERENCES exercices(id_exercise),
    FOREIGN KEY (id_program) REFERENCES programmes(id_program)
);

INSERT INTO exercises (id_exercise, nom, description) VALUES 
(1, 'Antilope', 'Description de l''exercice 1');

INSERT INTO programmes (id_program, nom, description) VALUES 
(1, 'VITESSE', 'Description du programme 1'),
(2, 'PUISSANCE', 'Description du programme 2'),
(3, 'ENDURANCE', 'Description du programme 3');

INSERT INTO exercices_programmes (id_exercise, id_program) VALUES 
(1, 1);