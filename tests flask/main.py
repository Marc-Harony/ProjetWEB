import hashlib


class Utilisateur:    
    
    def __init__(self, id, nom, email, password_input):
        self.id = id
        self.nom = nom
        self.email = email
        self.password_input = password_input
        self.password_hash = self.hashPass(password_input)
        self.caves = []

    def authentifierUser(self, email, password):
        
        return self.checkPass(password, self.password_hash)

    def ajouterCave(self, cave):
        self.caves.append(cave)

    def supprimerCave(self, cave):
        self.caves.remove(cave)

    def listerCaves(self):
        return self.caves

    def laisserCommentaire(self, bouteille, commentaire):
        bouteille.ajouterCommentaire(commentaire)

    def ajouterEtiquette(self, bouteille, etiquette):
        bouteille.ajouterEtiquette(etiquette)

    def supprimerEtiquette(self, bouteille):
        bouteille.supprimerEtiquette()

    def hashPass(self, password_input):
        # Create a new sha256 hash object
        hash_object = hashlib.sha256()

        # Add the password_input to the hash object
        hash_object.update(password_input.encode())

        # Get the hexadecimal representation of the hash
        password_hash = hash_object.hexdigest()

        return password_hash

    def checkPass(self, password_input, password_hash):
        # Comparez le mot de passe fourni avec le hash stocké
        return True

    def changerPass(self, ancien_password, nouveau_password):
        if self.checkPass(ancien_password, self.password_hash):
            self.password_hash = self.hashPass(nouveau_password)


class Cave:
    def __init__(self, id, nom, localisation, capacite):
        self.id = id
        self.nom = nom
        self.localisation = localisation
        self.capacite = capacite
        self.etageres = []

    def ajouterEtagere(self, etagere):
        self.etageres.append(etagere)

    def supprimerEtagere(self, etagere):
        self.etageres.remove(etagere)

    def listerEtageres(self):
        return self.etageres


class Etagere:
    def __init__(self, id, nom, capacite):
        self.id = id
        self.nom = nom
        self.capacite = capacite
        self.bouteilles = []

    def ajouterBouteille(self, bouteille):
        self.bouteilles.append(bouteille)

    def supprimerBouteille(self, bouteille):
        self.bouteilles.remove(bouteille)

    def listerBouteilles(self):
        return self.bouteilles

class Commentaire:
    def __init__(self, id, texte, auteur, note):
        self.id = id
        self.texte = texte
        self.auteur = auteur
        self.note = note


class Bouteille:
    def __init__(self, id, domaine, nom, type, annee, region, prix, etiquette):
        self.id = id
        self.domaine = domaine
        self.nom = nom
        self.type = type
        self.annee = annee
        self.region = region
        self.prix = prix
        self.etiquette = etiquette
        self.commentaires = []
        self.note_moyenne = 0.0
        self.quantite = 1

    def calculerNoteMoyenne(self):
        total_notes = sum(commentaire.note for commentaire in self.commentaires)
        self.note_moyenne = total_notes / len(self.commentaires) if self.commentaires else 0


#TEST

# Create an instance of the Utilisateur class
user = Utilisateur(1, 'Jean Bon', 'jean.bon@mail.com', 'motdepasse')

# Print the hashed password
print(f"This is the hashed password : {user.password_hash}")