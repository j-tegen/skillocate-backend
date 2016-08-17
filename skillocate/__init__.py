from flask import Flask, request, jsonify, abort, session, g
from flask.ext.httpauth import HTTPBasicAuth
from flask_sqlalchemy import SQLAlchemy
from functools import update_wrapper
import os
import skillocate.config
from elasticsearch import Elasticsearch
    

app = Flask(__name__)
app.secret_key = config.secret_key
app.config['SQLALCHEMY_DATABASE_URI'] = config.connection_string

print(app.config['SQLALCHEMY_DATABASE_URI'])
auth = HTTPBasicAuth()
db = SQLAlchemy(app)

from skillocate.models import *
from skillocate.views import *

db.create_all()
db.session.commit()

db.init_app(app)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in config.ALLOWED_EXTENSIONS

@auth.verify_password
def verify_password(email_or_token,password):
    # first try to authenticate by token
    print(email_or_token)
    user = User.verify_auth_token(email_or_token)
    if not user:
        # try to authenticate with username/password
        user = User.query.filter_by(email = email_or_token).first()
        if not user or not user.check_password(password):
            return False
    g.user = user
    return True

#DEPRECATED!?
@app.route('/api/token')
@auth.login_required
def get_auth_token():
    try:
        user = g.user
        print(user.generate_auth_token())
        token = g.user.generate_auth_token()
    except Exception as err:
        print(err)
    return jsonify({ 'token': token.decode('ascii') })




