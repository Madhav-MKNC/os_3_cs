# app.py
from utils import *
from flask import Flask, render_template, request, session, redirect, url_for
import os
import pandas as pd
from werkzeug.utils import secure_filename

from dotenv import load_dotenv
load_dotenv()

from utils import *

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filename)
            session['filename'] = filename
            return redirect(url_for('process'))
    return render_template('index.html')


@app.route('/process', methods=['GET', 'POST'])
def process():
    filename = session.get('filename')
    if not filename:
        return redirect(url_for('index'))

    if request.method == 'POST':
        records = get_records(filename)
        entries = get_interested_entries(records)
        return render_template('index.html', entries=entries, filename=filename)

    return render_template('index.html', filename=filename)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)
