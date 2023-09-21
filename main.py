from flask import Flask, redirect, request, flash, session
from flask import render_template
import os
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
import cv2
import pyrebase

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'webp', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
config = {
    'apiKey': "AIzaSyBw2dzPCQ7HZ8uKRbTcEBou7kFqLEg6jnI",
    'authDomain': "big-smile-editing.firebaseapp.com",
    'projectId': "big-smile-editing",
    'storageBucket': "big-smile-editing.appspot.com",
    'messagingSenderId': "702313137995",
    'appId': "1:702313137995:web:fb66a74d60617b54ba0ace",
    'measurementId': "G-9DQMG7RHTE",
    'databaseURL': ''
}
firebase = pyrebase.initialize_app(config)
auth = firebase.auth()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
def processImage(filename,operation):
    print(f"the operation is {operation} and file name is {filename}")
    img = cv2.imread(f"uploads/{filename}")
    match operation:
        case "cgray":
            imgProcessed = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
            newFilename = f"static/{filename}"
            cv2.imwrite(newFilename,imgProcessed)
            return newFilename
        case "cwebp":
            newFilename = f"static/{filename.split('.')[0]}.webp"
            cv2.imwrite(newFilename,img)
            return newFilename
        case "cjpg":
            newFilename = f"static/{filename.split('.')[0]}.jpg"
            cv2.imwrite(newFilename,img)
            return newFilename
        case "cpng":
            newFilename = f"static/{filename.split('.')[0]}.png"
            cv2.imwrite(newFilename,img)
            return newFilename
    pass 

@app.route('/',methods=['POST','GET'])
def index():
    if('user' in session):
        return "Hi, {}".format(session['user'])
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        try:
            user = auth.sign_in_with_email_and_password(email,password)
            session['user'] = email
            return redirect('/index')
        except:
            return 'Failed to login'
    return render_template('home.html')
@app.route('/logout')
def logout():
    session.pop('user')
    return redirect('/')
@app.route('/index')
def home():
    return render_template('index.html')
@app.route('/about')
def about():
    return render_template('about.html')
@app.route('/edit',methods=["GET","POST"])
def edit():
    if request.method=="POST":
        operation = request.form.get("op")
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return 'error'
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return 'error no selected file'
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            new = processImage(filename,operation)
            flash(f"Your image has been processed and is available <a href='/{new}' target='_blank'> here </a>")
            return render_template('index.html')
    return render_template('index.html')

app.run(debug=True)