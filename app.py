from flask import Flask, redirect, url_for, session, render_template, flash, request
from authlib.integrations.flask_client import OAuth
from flask_mysqldb import MySQL
from bs4 import BeautifulSoup
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Genera una chiave segreta per la gestione delle sessioni

# Configura MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')  # Username di MySQL
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')  # Password di MySQL
app.config['MYSQL_DB'] = os.getenv('MYSQL_NAME')  # Password di MySQL
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)  # Inizializza l'estensione MySQL

# Configura OAuth
oauth = OAuth(app)
github = oauth.register(
    name='github',
    client_id=os.getenv('GITHUB_CLIENT_ID'),  # Client ID di GitHub
    client_secret=os.getenv('GITHUB_CLIENT_SECRET'),  # Client secret di GitHub
    authorize_url='https://github.com/login/oauth/authorize',  # URL di autorizzazione di GitHub
    authorize_params=None,
    access_token_url='https://github.com/login/oauth/access_token',  # URL per ottenere il token di accesso
    access_token_params=None,
    refresh_token_url=None,
    redirect_uri='http://localhost:5000/callback',  # URL di reindirizzamento dopo l'autorizzazione
    client_kwargs={'scope': 'user:email'},  # Scopi richiesti
)

# Limite dimensione file in byte (3 MB)
MAX_FILE_SIZE = 3 * 1024 * 1024

# Funzione per pulire il contenuto del file rimuovendo tag script e style
def clean_content(content):
    soup = BeautifulSoup(content, 'lxml')
    for script in soup(["script", "style"]):
        script.decompose()
    return soup.get_text()

# Rotta per la home page
@app.route('/')
def home():
    return render_template('home.html')  # Renderizza il template home.html

# Rotta per il login
@app.route('/login')
def login():
    return github.authorize_redirect(url_for('authorize', _external=True))  # Reindirizza alla pagina di autorizzazione di GitHub

# Rotta per gestire il callback di GitHub
@app.route('/callback')
def authorize():
    try:
        token = github.authorize_access_token()  # Ottiene il token di accesso
        resp = github.get('https://api.github.com/user', token=token)  # Ottiene le informazioni sull'utente
        profile = resp.json()
        session['profile'] = profile  # Memorizza il profilo dell'utente nella sessione
        return redirect(url_for('profile'))  # Reindirizza alla pagina del profilo
    except Exception as e:
        print(e)
        flash('Autenticazione fallita.')  # Mostra un messaggio di errore se l'autenticazione fallisce
        return redirect(url_for('home'))

# Rotta per il profilo utente
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    profile = session.get('profile')
    if not profile:
        return redirect(url_for('home'))  # Se il profilo non è presente nella sessione, reindirizza alla home

    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Nessun file selezionato')
            return redirect(url_for('profile'))

        file = request.files['file']
        if file.filename == '':
            flash('Nessun file selezionato')
            return redirect(url_for('profile'))

        if not file.filename.endswith('.txt'):
            flash('Sono permessi solo file .txt')
            return redirect(url_for('profile'))

        file.seek(0, os.SEEK_END)
        file_length = file.tell()
        file.seek(0, 0)
        
        if file_length > MAX_FILE_SIZE:
            flash('Il file è troppo grande. Il limite è 3 MB.')
            return redirect(url_for('profile'))

        filename = file.filename
        content = file.read().decode('utf-8')
        cleaned_content = clean_content(content)  # Pulisce il contenuto del file
        uploaded_by = profile['login']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO files (filename, content, uploaded_by) VALUES (%s, %s, %s)", (filename, cleaned_content, uploaded_by))
        mysql.connection.commit()
        cur.close()

        flash('File caricato con successo!')
        return redirect(url_for('profile'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM files")
    files = cur.fetchall()
    cur.close()

    return render_template('profile.html', profile=profile, files=files)

# Rotta per il logout
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
