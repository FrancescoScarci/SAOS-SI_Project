from flask import Flask, redirect, url_for, session, render_template, flash, request
from authlib.integrations.flask_client import OAuth
from flask_mysqldb import MySQL
from bs4 import BeautifulSoup
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configura MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'  # Inserisci il tuo username MySQL
app.config['MYSQL_PASSWORD'] = '0000'  # Inserisci la tua password MySQL
app.config['MYSQL_DB'] = 'flask_app'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

# Configura OAuth
oauth = OAuth(app)
github = oauth.register(
    name='github',
    client_id='Ov23liDzKhFGdab5KWTH',  # Sostituisci con il tuo client ID
    client_secret='d4d652fd6f392260859248676d4205daf8dc8971',  # Sostituisci con il tuo client secret
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

def clean_content(content):
    soup = BeautifulSoup(content, 'lxml')
    for script in soup(["script", "style"]):
        script.decompose()
    return soup.get_text()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login')
def login():
    return github.authorize_redirect(url_for('authorize', _external=True))

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

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    profile = session.get('profile')
    if not profile:
        return redirect(url_for('home'))

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
        cleaned_content = clean_content(content)
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

@app.route('/logout')
def logout():
    session.pop('profile', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)


#PROVAAAAAAA