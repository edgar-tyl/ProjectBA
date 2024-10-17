
import os
from flask import (
    Blueprint,  render_template, request, jsonify
)


from .AiHandler import AiHandler


ai = AiHandler(os.path.join("."), True, False, False)
bp = Blueprint('chat', __name__)

#landing page, includes chat prompt 
@bp.route('/', methods=('GET', 'POST'))
def index():
    return render_template("index.html")

#used when user submits question. Uses AiHandler to answer question and send answer back to client
@bp.route('/submit', methods = ['GET', 'POST'])
def submit():  
    data = ai.runTask(request.form['text'])
    return jsonify(question = data["question"],
                   query = data["query"],
                   table = data["table"],
                   answer = data["answer"])

