from flask import Flask
from flask_mysqldb import MySQL
from authlib.integrations.flask_client import OAuth

app = Flask(__name__)
app.config.from_object('config.Config')

mysql = MySQL(app)
oauth = OAuth(app)

from routes import *

if __name__ == '__main__':
    app.run(debug=True)
