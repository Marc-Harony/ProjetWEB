-- Insertion of a new bottle
INSERT INTO bouteilles (domaine, nom, type, annee, region, prix, etiquette, note_moyenne, quantite)
VALUES ('Baron Philippe de Rothschild ', 'Mouton Cadet', 'Rouge', 2022, 'Bordeaux', 10.5, 'Etiquette Test', 4.5, 1);

-- Update of the quantity of the bottle
UPDATE bouteilles
SET quantite = quantite + 1
WHERE domaine = 'Baron Philippe de Rothschild ' AND nom = 'Mouton Cadet' AND type = 'Rouge' AND annee = 2022 AND region = 'Bordeaux';


-- Add Bottles

INSERT INTO bouteilles (domaine, nom, type, annee, region, prix, etiquette)
VALUES ('Mouton Cadet', 'Baron Philippe de Rothschild', 'Rouge', 2019, 'Bordeaux', 20.00, 'chemin/vers/etiquette.jpg')
ON CONFLICT (domaine, nom, type, annee, region) DO UPDATE
SET quantite = bouteilles.quantite + 1;
