-- Création de la table 'utilisateurs'
CREATE TABLE utilisateurs (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    mot_de_passe_hache VARCHAR(255) NOT NULL
);

-- Création de la table 'commentaires'
CREATE TABLE commentaires (
    id SERIAL PRIMARY KEY,
    texte TEXT NOT NULL,
    note FLOAT CHECK (note >= 0 AND note <= 20),
    date_commentaire DATE NOT NULL DEFAULT CURRENT_DATE,
    auteur_id INTEGER REFERENCES utilisateurs(id)
);

-- Création de la table 'bouteilles'
CREATE TABLE bouteilles (
    id SERIAL PRIMARY KEY,
    domaine VARCHAR(255) NOT NULL,
    nom VARCHAR(255) NOT NULL,
    type VARCHAR(255) NOT NULL,
    annee INTEGER CHECK (annee > 0),
    region VARCHAR(255) NOT NULL,
    prix FLOAT CHECK (prix >= 0),
    etiquette TEXT,
    note_moyenne FLOAT CHECK (note_moyenne >= 0 AND note_moyenne <= 5) DEFAULT 0,
    quantite INTEGER CHECK (quantite >= 0) DEFAULT 0,
    UNIQUE (domaine, nom, type, annee, region)
);

-- Création de la table 'caves'
CREATE TABLE caves (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(255) NOT NULL,
    localisation VARCHAR(255),
    capacite INTEGER CHECK (capacite >= 0),
    utilisateur_id INTEGER REFERENCES utilisateurs(id)
);

-- Création de la table 'etageres'
CREATE TABLE etageres (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(255) NOT NULL,
    capacite INTEGER CHECK (capacite >= 0),
    cave_id INTEGER REFERENCES caves(id)
);

-- Association entre bouteilles et étagères (supposant qu'une bouteille ne peut appartenir qu'à une seule étagère)
CREATE TABLE bouteilles_etageres (
    bouteille_id INTEGER REFERENCES bouteilles(id),
    etagere_id INTEGER REFERENCES etageres(id),
    PRIMARY KEY (bouteille_id, etagere_id)
);

INSERT INTO utilisateurs (nom, email, mot_de_passe_hache) 
VALUES ('Jean', 'Jean@bon.com', 'motdepassehache');