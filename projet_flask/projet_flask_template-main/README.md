# projet_flask_template
projet_flask_template pour les collegues


 <h2>BIBLIOTHEQUES</h2>
 
install these python pip libraries :


 <ul>
        <li>
            <b>pip install flask</b>
        </li>
         <li>
            <b>pip install mysql-connector-python</b>
        </li>
    </ul>

 <h2>BASE DE DONNEES</h2>

 Créer une base de donnees : utilisateurs_db

 Créer deux tables : utilisateurs et employes

 CREATE DATABASE utilisateurs_db;

CREATE TABLE utilisateurs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    utilisateur VARCHAR(50) NOT NULL,
    motdepasse VARCHAR(50) NOT NULL
);

INSERT INTO utilisateurs (utilisateur, motdepasse) VALUES ('admin', 'admin123');


CREATE TABLE employes (
    matricule INT AUTO_INCREMENT PRIMARY KEY,
    firstname VARCHAR(50) NOT NULL,
    lastname VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    role VARCHAR(50),
    phone VARCHAR(15)
);




 ![image](https://github.com/user-attachments/assets/e5b10663-573c-44ac-80f3-c9e59c266f8d)

 ![image](https://github.com/user-attachments/assets/5830663a-50ee-43df-9e38-a0ba7953c7cf)

![image](https://github.com/user-attachments/assets/e229faf8-edd6-4032-9edd-db6e495a7e1b)

![image](https://github.com/user-attachments/assets/3ebc3111-9d04-425a-83f3-3d6623cf7fa7)


