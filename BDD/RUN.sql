-- MySQL Script generated by MySQL Workbench
-- Wed Jun 26 10:28:46 2024
-- Model: New Model    Version: 1.0
-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `mydb` DEFAULT CHARACTER SET utf8 ;
USE `mydb` ;

-- -----------------------------------------------------
-- Table `mydb`.`users`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mydb`.`users` (
  iduser INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  firstname VARCHAR(45) NULL,
  surname VARCHAR(45) NULL,
  email VARCHAR(45) NULL,
  password_hash VARCHAR(60) NULL,
  weight FLOAT NULL,
  height FLOAT NULL,
  animal VARCHAR(45) NULL)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `mydb`.`exercises`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mydb`.`exercises` (
  id_exercise INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  description TEXT,
  time INT,
  distance INT,
  target_desc TEXT,
  target_result INT,
  completed BOOLEAN)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `mydb`.`program`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mydb`.`program` (
  id_program INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  description TEXT,
  completed BOOLEAN)
ENGINE = InnoDB;

USE `mydb` ;

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

-- -----------------------------------------------------
-- Placeholder table for view `mydb`.`view1`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mydb`.`view1` (`id` INT);

-- -----------------------------------------------------
-- View `mydb`.`view1`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `mydb`.`view1`;
USE `mydb`;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
