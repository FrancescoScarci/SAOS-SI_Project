La seguente applicazione fornisce all'utente un sito web nel quale caricare una proposta progettuale in formato .txt. Sul caricamento vengo effettuate delle verifiche in cui controllare se il file che si sta caricando è realmente un file .txt
 e non un tipo di file differente. In più è effettuato un controllo sulla dimensione del file (non deve superare i 3 mb). In più vi è un controllo sul contenuto nella quale vengono rimossi eventuali tag javascript per evitare possibili attacchi.

 Per accedere all'applicazione bisogna autenticarsi facendo login attraverso le proprie credenziali github utilizzando un login federato con OAuth2.

Per la realizzazione del progetto si è utilizzato Flask che è un micro framework web scritto in Python. È classificato come microframework perché non richiede strumenti o librerie particolari.

Si è preparato l'ambiente di lavoro installando python e usando come IDE Visual Studio Code ed installando le libreire necessarei

1) Crea un nuovo ambiente virtuale:
``` bash
python -m venv venv
.venv\Scripts\activate
```



2) Installa Flask e Authlib:
``` bash
pip install flask authlib
```



3) Nelle impostazioni di github, nella sezione sviluppatore, si può selezionare l'opzione "OAuth2 Apps" per poter richiedere il 'Client ID'  e 'Client secrets' per poter usufruire del login tramite github:
![Screenshot_20240529_180405](https://github.com/FrancescoScarci/SAOS-SI_Project/assets/170801341/7f72ff28-55ef-4934-a4e8-3ba1bfb43b30)


4) I file .txt sono stati salvati all'interno di un database mysql. Installare le librerie necessarie per collegare l'applicazione al database:
``` bash
pip install flask-mysqldb
```
Il db conterrà una tabella denominata "files" in cui saranno memorizzati:
-ID del file usato come chiave primaria
-Nome del file
-Il contenuto del file
-Quale utente ha caricato il file
-L'arco temporale in cui il file è stato caricato
``` bash
DROP DATABASE IF EXISTS flask_app;

CREATE DATABASE IF NOT EXISTS flask_app;

USE flask_app;

CREATE TABLE files (
    id INT AUTO_INCREMENT PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    uploaded_by VARCHAR(255) NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE USER 'username'@'localhost' IDENTIFIED BY 'password';


GRANT INSERT ON flask_app.files TO 'username'@'localhost';
GRANT SELECT ON flask_app.files TO 'username'@'localhost';
```


5) La web-app è strutturata nella seguente maniera:

**config.py**
``` bash
import os

class Config:
    SECRET_KEY = os.urandom(24)
    MYSQL_HOST = 'localhost'
    MYSQL_USER = os.getenv('MYSQL_USER')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
    MYSQL_DB = os.getenv('MYSQL_NAME')
    MYSQL_CURSORCLASS = 'DictCursor'
    GITHUB_CLIENT_ID = os.getenv('GITHUB_CLIENT_ID')
    GITHUB_CLIENT_SECRET = os.getenv('GITHUB_CLIENT_SECRET')
```
Qui sono inserite le credenziali del database (esername e password) ed il client_id e  il client_secret di github. Il tutto è stato inserito come variabile d'ambiente di windows per evitare l'inserimento in chiaro delle info sensibili all'interno del codice sorgente:

![image](https://github.com/FrancescoScarci/SAOS-SI_Project/assets/170801341/bc0ecc3d-73c0-4d31-aa72-e14098857145)  

**utils.py**
``` bash
from bs4 import BeautifulSoup

def clean_content(content):
    soup = BeautifulSoup(content, 'lxml')
    for script in soup(["script", "style"]):
        script.decompose()
    return soup.get_text()
```
Questo codice si occupa della pulizia del file, rimuovendo eventuali tag non consoni per evitare inizieno di codice malevo che potrebbero intaccare il corretto funzionamento del sistema
