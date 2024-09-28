
import os
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify, Response
)
from werkzeug.security import check_password_hash, generate_password_hash

from .AiHandler import AiHandler


ai = AiHandler(os.path.join(".", "ProjectBA"), True, True, True)
bp = Blueprint('chat', __name__)

#landing page, includes chat prompt 
@bp.route('/', methods=('GET', 'POST'))
def index():
    return render_template("index.html")

#used when user submits question. Uses AiHandler to answer question and send answer back to client
@bp.route('/submit', methods = ['GET', 'POST'])
def submit():  
    return jsonify(message = ai.runTask(request.form['text']))

