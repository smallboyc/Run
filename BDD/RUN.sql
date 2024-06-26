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

CREATE TABLE exercices (
    id_exercice INT PRIMARY KEY,
    nom VARCHAR(100),
    description TEXT
);

CREATE TABLE programmes (
    id_programme INT PRIMARY KEY,
    nom VARCHAR(100),
    description TEXT
);

CREATE TABLE exercices_programmes (
    id_exercice INT,
    id_programme INT,
    PRIMARY KEY (id_exercice, id_programme),
    FOREIGN KEY (id_exercice) REFERENCES exercices(id_exercice),
    FOREIGN KEY (id_programme) REFERENCES programmes(id_programme)
);

INSERT INTO exercices (id_exercice, nom, description) VALUES 
(1, 'Antilope', 'Description de l''exercice 1');

INSERT INTO programmes (id_programme, nom, description) VALUES 
(1, 'VITESSE', 'Description du programme 1'),
(2, 'PUISSANCE', 'Description du programme 2'),
(3, 'ENDURANCE', 'Description du programme 3');

INSERT INTO exercices_programmes (id_exercice, id_programme) VALUES 
(1, 1);
