import os
import pandas as pd 

from flask import Flask, flash, request, redirect, render_template, Markup
from werkzeug.utils import secure_filename
from octo import octo

app=Flask(__name__)

app.secret_key = "secret key"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

path = os.getcwd()
UPLOAD_FOLDER = os.path.join(path, 'uploads')

if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = set(['xlsx'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def upload_form():
    return render_template('upload.html')


@app.route('/', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash('No file selected for uploading')
            return redirect(request.url)
            
        if file and allowed_file(file.filename):

            formula = octo(request.files.get('file'))
            flash(formula)

            return redirect(request.url)

        else:
            flash('Allowed file types are: .xlsx')
            return redirect(request.url)


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5500, debug=False)