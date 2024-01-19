from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, upgrade

from models import db

 
app = Flask(__name__)
app.config.from_object('config.ConfigDebug')

db.app = app
db.init_app(app)
migrate = Migrate(app,db)


if __name__  == "__main__":
    with app.app_context():
        upgrade()
        #seedData(db)
    
    app.run(debug=True)
