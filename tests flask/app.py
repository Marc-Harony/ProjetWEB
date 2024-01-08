from flask import Flask, session, redirect, url_for, request, render_template, flash
import psycopg2


app = Flask(__name__)
app.secret_key = 'bonjour'  # Remplacer avec une vraie clé secrète

def get_db_connection():
    conn = psycopg2.connect(
        host="185.207.251.192",
        database="prjcave",
        user="mharony",
        password="CompoteDeP0mme"
    )
    return conn
    
@app.route('/list_user', methods=['POST'])
def list_users():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM utilisateurs")
    users = cur.fetchall()
    print(users)
    conn.close()
    return render_template('users.html', users=users)

@app.route('/list_bottles', methods=['POST'])
def list_bottles():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM bouteilles")
    bottles = cur.fetchall()
    print(bottles)
    conn.close()
    return render_template('bouteilles.html', bottles=bottles)


@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')


@app.route('/hello', methods=['POST'])
def hello():
    name = request.form.get('name')
    return f'Hello {name}'


@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ''  # Variable pour stocker le message

    if request.method == 'POST':
        # Récupération des identifiants depuis le formulaire
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cur = conn.cursor()

        # Vérifier si l'utilisateur existe dans la base de données
        cur.execute("SELECT id, nom, mot_de_passe_hache FROM utilisateurs WHERE email = %s", (email,))
        user = cur.fetchone()

        # Fermer la connexion à la base de données
        cur.close()
        conn.close()

        # Comparer les identifiants et le mot de passe (sans hachage pour le moment)
        if user and user[2] == password:
            session['user_id'] = user[0]
            session['user_nom'] = user[1]
            return redirect(url_for('dashboard'))
        else:
            message = 'No user' if not user else f'Bonjour {user[1]}'

    return render_template('login.html', message=message)

@app.route('/logout')
def logout():
    # Suppression de l'utilisateur de la session
    session.pop('user_id', None)
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    # Vérification si l'utilisateur est connecté
    if 'user_id' in session:
        return render_template('dashboard.html')
    else:
        return redirect(url_for('login'))


@app.route('/mes_caves')
def mes_caves():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nom, localisation, capacite FROM caves WHERE utilisateur_id = %s", (user_id,))
    caves = cur.fetchall()
    print(caves)  # Debug: imprimer les caves pour vérifier les données
    cur.close()
    conn.close()

    return render_template('mes_caves.html', caves=caves)


# Ajouter une route pour créer un compte
# @app.route('/create_account', methods=['GET', 'POST'])
# def create_account():
#     message = ''
#     if request.method == 'POST':
#         nom = request.form['nom']
#         email = request.form['email']
#         mot_de_passe = request.form['mot_de_passe']
#         # mot_de_passe_hache = request.form['mot_de_passe_hache']
#         conn = get_db_connection()
#         cur = conn.cursor()
#         cur.execute("SELECT id FROM utilisateurs WHERE email = %s", (email,))
#         user = cur.fetchone()
#         if user:
#             message = 'L\'utilisateur existe déjà'
#         else:
#             cur.execute("""INSERT INTO utilisateurs (nom, email, mot_de_passe) 
#                 VALUES (%s, %s, %s, %s)""", (nom, email, mot_de_passe))
#             conn.commit()
#             cur.close()
#             conn.close()
#             return redirect(url_for('login'))

@app.route('/ajouter_cave', methods=['GET', 'POST'])
def ajouter_cave():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        nom = request.form['nom']
        localisation = request.form['localisation']
        capacite = int(request.form['capacite'])  # Convertir la capacité AAen entier

        conn = get_db_connection()
        cur = conn.cursor()
        # Insertion de la nouvelle cave
        cur.execute("""
            INSERT INTO caves (nom, localisation, capacite, utilisateur_id) 
            VALUES (%s, %s, %s, %s) RETURNING id
            """, (nom, localisation, capacite, session['user_id']))
        # Récupération de l'ID de la nouvelle cave
        new_cave_id = cur.fetchone()[0]
        # Création des étagères pour la nouvelle cave
        for i in range(capacite):
            cur.execute("""
                INSERT INTO etageres (nom, capacite, cave_id) 
                VALUES (%s, %s, %s)
                """, (f'Étagère {i+1}', 10, new_cave_id))  # Vous pouvez ajuster la capacité de chaque étagère si nécessaire
        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for('mes_caves'))
    return render_template('ajouter_cave.html')

@app.route('/ajouter_bouteille_etagere/<int:cave_id>', methods=['POST'])
def ajouter_bouteille_etagere(cave_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    bouteille_id = request.form.get('bouteille_id')
    etagere_id = request.form.get('etagere_id')
    quantite = int(request.form.get('quantite'))
    user_id = session['user_id']

    conn = get_db_connection()
    cur = conn.cursor()

    # Vérifiez la quantité de bouteilles disponibles dans 'bouteilles'
    cur.execute("SELECT quantite FROM bouteilles WHERE id = %s", (bouteille_id,))
    bouteille_info = cur.fetchone()
    if not bouteille_info or quantite > bouteille_info[0]:
        cur.close()
        conn.close()
        return "Quantité insuffisante dans le stock."

    # Vérifiez la capacité disponible sur l'étagère dans 'mes_bouteilles'
    cur.execute("SELECT COUNT(*) FROM mes_bouteilles WHERE etagere_id = %s", (etagere_id,))
    quantite_existante = cur.fetchone()[0] or 0
    capacite_etagere = 10  # La capacité fixe de chaque étagère

    # Calculer la quantité réelle à ajouter en fonction de l'espace disponible
    quantite_a_ajouter = min(quantite, capacite_etagere - quantite_existante)
    quantite_restante = quantite - quantite_a_ajouter

    # Ajouter les bouteilles à l'étagère une par une
    for _ in range(quantite_a_ajouter):
        cur.execute("""
            INSERT INTO mes_bouteilles (bouteille_id, proprietaire_id, etagere_id, cave_id) 
            VALUES (%s, %s, %s, %s)
            """, (bouteille_id, user_id, etagere_id, cave_id))
    
    # Mettre à jour la quantité de bouteilles dans 'bouteilles'
    nouvelle_quantite = bouteille_info[0] - quantite_a_ajouter
    cur.execute("UPDATE bouteilles SET quantite = %s WHERE id = %s", (nouvelle_quantite, bouteille_id))
    
    conn.commit()
    cur.close()
    conn.close()

    # Rediriger vers la page de gestion de la cave, avec un message si besoin
    if quantite_restante > 0:
        flash(f"Seules {quantite_a_ajouter} bouteilles ont été ajoutées. Il n'y avait pas assez d'espace pour les {quantite_restante} autres.")
    return redirect(url_for('gerer_cave', cave_id=cave_id))



@app.route('/supprimer_cave/<int:cave_id>', methods=['POST'])
def supprimer_cave(cave_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()
    # Assurez-vous d'abord de supprimer toutes les étagères associées à la cave
    cur.execute("DELETE FROM etageres WHERE cave_id = %s", (cave_id,))
    # Ensuite, supprimez la cave
    cur.execute("DELETE FROM caves WHERE id = %s AND utilisateur_id = %s", (cave_id, session['user_id']))
    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for('mes_caves'))


@app.route('/gerer_cave/<int:cave_id>', methods=['GET', 'POST'])
def gerer_cave(cave_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    session['cave_id'] = cave_id
    conn = get_db_connection()
    cur = conn.cursor()

    # Récupérer les étagères pour cette cave
    cur.execute("SELECT id, nom FROM etageres WHERE cave_id = %s", (cave_id,))
    etageres = cur.fetchall()
    
    # Récupérer les bouteilles disponibles
    cur.execute("SELECT id, domaine, nom, annee FROM bouteilles")
    bouteilles_disponibles = cur.fetchall()

    #On récupère le nom de la cave
    cur.execute("SELECT nom FROM caves WHERE id = %s AND utilisateur_id = %s", (cave_id, user_id))
    cave_nom = cur.fetchone()[0]

    # Récupérer les bouteilles pour chaque étagère
    bouteilles_par_etagere = {}
    bouteilles_par_etagere = {}
    for etagere in etageres:
        etagere_id = etagere[0]
        cur.execute("""
            SELECT mb.id, b.domaine, b.nom, b.annee, b.quantite
            FROM mes_bouteilles mb
            JOIN bouteilles b ON b.id = mb.bouteille_id
            WHERE mb.etagere_id = %s
            """, (etagere_id,))
        bouteilles_par_etagere[etagere_id] = [{
            'id': row[0],
            'domaine': row[1],
            'nom': row[2],
            'annee': row[3],
            'quantite': row[4]
        } for row in cur.fetchall()]

    cur.close()
    conn.close()

    return render_template('gerer_cave.html',cave_nom=cave_nom, etageres=etageres, bouteilles_disponibles=bouteilles_disponibles, bouteilles_par_etagere=bouteilles_par_etagere, cave_id=cave_id)


@app.route('/supprimer_bouteille/<int:bouteille_id>', methods=['POST'])
def supprimer_bouteille(bouteille_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    conn = get_db_connection()
    cur = conn.cursor()

    # Récupérer l'ID de la bouteille dans la table bouteilles et augmenter la quantité
    cur.execute("SELECT bouteille_id FROM mes_bouteilles WHERE id = %s AND proprietaire_id = %s", (bouteille_id, user_id))
    bouteille_originale_id = cur.fetchone()
    if bouteille_originale_id:
        bouteille_originale_id = bouteille_originale_id[0]
        # Augmenter la quantité dans bouteilles
        cur.execute("UPDATE bouteilles SET quantite = quantite + 1 WHERE id = %s", (bouteille_originale_id,))

        # Supprimer la bouteille de mes_bouteilles
        cur.execute("DELETE FROM mes_bouteilles WHERE id = %s AND proprietaire_id = %s", (bouteille_id, user_id))

    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for('gerer_cave', cave_id=session['cave_id']))

@app.route('/vider_etagere/<int:etagere_id>', methods=['POST'])
def vider_etagere(etagere_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    conn = get_db_connection()
    cur = conn.cursor()

    # Récupérer toutes les bouteilles de l'étagère
    cur.execute("SELECT bouteille_id, COUNT(*) FROM mes_bouteilles WHERE etagere_id = %s AND proprietaire_id = %s GROUP BY bouteille_id", (etagere_id, user_id))
    bouteilles = cur.fetchall()

    for bouteille_id, quantite in bouteilles:
        # Augmenter la quantité dans bouteilles
        cur.execute("UPDATE bouteilles SET quantite = quantite + %s WHERE id = %s", (quantite, bouteille_id))

    # Supprimer toutes les bouteilles de l'étagère dans mes_bouteilles
    cur.execute("DELETE FROM mes_bouteilles WHERE etagere_id = %s AND proprietaire_id = %s", (etagere_id, user_id))

    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for('gerer_cave', cave_id=session['cave_id']))



def verify_user(username, password):
    # Implémentez votre logique de vérification des identifiants ici
    pass


if __name__ == '__main__':
    app.run(debug=True)
    
