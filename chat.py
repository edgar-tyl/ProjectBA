import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify, Response
)
from werkzeug.security import check_password_hash, generate_password_hash

from .AiHandler import AiHandler


ai = AiHandler()
bp = Blueprint('chat', __name__)

@bp.route('/', methods=('GET', 'POST'))
def index():
    return render_template("index.html")

@bp.route('/hello')
def hello():
    return jsonify(message="Hello, World")

@bp.route('/submit', methods = ['GET', 'POST'])
def submit():  
    return jsonify(message = ai.createRetrievalChain(request.form['text']))

