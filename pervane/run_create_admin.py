"""This is a hack for fab to create an admin user in app.db for us.

Since everything about pervane is in run.py and it has its own argparse,
it keeps conflicting with flask fab create-admin command.

This is a proxy app just to run the create-admin command.

export FLASK_APP="run_create_admin"; flask fab create-admin
"""

"""
from flask import Flask
from flask_appbuilder import AppBuilder, SQLA

app = Flask(__name__, template_folder='templates_bulma')
db = SQLA(app)
appbuilder = AppBuilder(app, db.session)
"""

import os
from flask import Flask
from flask_appbuilder import SQLA, AppBuilder

# init Flask
app = Flask(__name__)

# Basic config with security for forms and session cookie
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
app.config['CSRF_ENABLED'] = True
app.config['SECRET_KEY'] = 'thisismyscretkey'

# Init SQLAlchemy
db = SQLA(app)
# Init F.A.B.
appbuilder = AppBuilder(app, db.session)

# Run the development server
app.run(host='0.0.0.0', port=8083, debug=True)
