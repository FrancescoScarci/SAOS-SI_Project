from flask import Flask, redirect, url_for, session, render_template, flash, request
from authlib.integrations.flask_client import OAuth
from flask_mysqldb import MySQL
from bs4 import BeautifulSoup
import os

app = Flask(__name__)
app.secret_key = os.urandom(24) #Configura una chiave segreta per la gestione delle sessioni.

# Configura MySQL usando le variabili di ambiente
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')  # Username di MySQL
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')  # Password di MySQL
app.config['MYSQL_DB'] = os.getenv('MYSQL_NAME')  # Nome del database MySQL
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

# Configura OAuth usando le variabili di ambiente
oauth = OAuth(app)
github = oauth.register(
    name='github',
    client_id=os.getenv('GITHUB_CLIENT_ID'),  # Client ID di GitHub
    client_secret=os.getenv('GITHUB_CLIENT_SECRET'),  # Client secret di GitHub
    authorize_url='https://github.com/login/oauth/authorize',
    authorize_params=None,
    access_token_url='https://github.com/login/oauth/access_token',
    access_token_params=None,
    refresh_token_url=None,
    redirect_uri='http://localhost:5000/callback',
    client_kwargs={'scope': 'user:email'},
)

# Limite dimensione file in byte (3 MB)
MAX_FILE_SIZE = 3 * 1024 * 1024

#Utilizza BeautifulSoup per rimuovere script e stili da un contenuto HTML
def clean_content(content):
    soup = BeautifulSoup(content, 'lxml')
    for script in soup(["script", "style"]):
        script.decompose()
    return soup.get_text()

#Definisce la rotta per la homepage, rendendo il template home.html
@app.route('/')
def home():
    return render_template('home.html')

#Definisce la rotta per il login, reindirizzando l'utente a GitHub per l'autenticazione OAuth
@app.route('/login')
def login():
    return github.authorize_redirect(url_for('authorize', _external=True))

#Gestisce il callback di GitHub, ottiene il token di accesso, recupera il profilo utente e lo salva nella sessione
@app.route('/callback')
def authorize():
    try:
        token = github.authorize_access_token()
        resp = github.get('https://api.github.com/user', token=token)
        profile = resp.json()
        session['profile'] = profile
        return redirect(url_for('profile'))
    except Exception as e:
        print(e)
        flash('Autenticazione fallita.')
        return redirect(url_for('home'))

#Definisce la rotta per il profilo utente
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    profile = session.get('profile') # Recupera le informazioni del profilo dalla sessione. 
    if not profile:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        if 'file' not in request.files:  # Controlla se nel form inviato è presente un file
            flash('Nessun file selezionato') # flash('Nessun file selezionato'): Mostra un messaggio di errore all'utente.
            return redirect(url_for('profile')) # return redirect(url_for('profile')): Reindirizza nuovamente alla pagina del profilo
        
        #Verifica dell'nome del File
        file = request.files['file'] 
        if file.filename == '':
            flash('Nessun file selezionato')
            return redirect(url_for('profile'))
        
        #verifica estensione
        if not file.filename.endswith('.txt'):
            flash('Sono permessi solo file .txt')
            return redirect(url_for('profile'))

        file.seek(0, os.SEEK_END)
        file_length = file.tell()
        file.seek(0, 0)
        
        #verifica dimensione
        if file_length > MAX_FILE_SIZE:
            flash('Il file è troppo grande. Il limite è 3 MB.')
            return redirect(url_for('profile'))

        filename = file.filename
        content = file.read().decode('utf-8')
        cleaned_content = clean_content(content)
        uploaded_by = profile['login']
        
        #caricamento su db
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO files (filename, content, uploaded_by) VALUES (%s, %s, %s)", (filename, cleaned_content, uploaded_by))
        mysql.connection.commit()
        cur.close()

        flash('File caricato con successo!')
        return redirect(url_for('profile'))

    #get di tutta la tabella
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM files")
    files = cur.fetchall()
    cur.close()

    return render_template('profile.html', profile=profile, files=files)

# Definisce la rotta per il logout, rimuovendo le informazioni del profilo dalla sessione e reindirizzando l'utente alla homepage
@app.route('/logout')
def logout():
    session.pop('profile', None)  # Rimuove la chiave 'profile' dalla sessione
    session.clear()  # Cancella tutte le chiavi nella sessione per sicurezza
    
    # Crea una risposta di reindirizzamento alla homepage del tuo sito
    home_url = url_for('home', _external=True)
    
    # Reindirizza l'utente alla homepage di GitHub con un parametro di query che riporta l'utente al tuo sito
    github_logout_url = f'https://github.com/logout?returnTo={home_url}'
    
    return redirect(github_logout_url)

if __name__ == '__main__':
    app.run(debug=True)  # Avvia l'applicazione Flask in modalità debug
