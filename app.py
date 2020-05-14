from flask import Flask, render_template,request,send_file,jsonify, redirect, session, jsonify
from audio_encrpy import Steganography
from audio_decrpy import Steganaograpy_decryption
#from image_encrpy import Steganography
#from image_decrpy import Steganaograpy_decryption
import os
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime



app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

class Encrypted(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(80), nullable=False)
    date = db.Column(db.String(80), nullable=False)
    allowed = db.Column(db.String(120), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('users', lazy=True))

    def __repr__(self):
        return '<User %r>' % self.username


db.create_all()
app.config['UPLOAD_FOLDER'] = './uploads'
app.secret_key = 'dsdsds34567890'
app.config['EXTENSIONS'] = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','wav'}



@app.route('/signup', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        form = request.form

        user = User(username = form.get('username'), password = form.get('password'), email = form.get('email'))

        db.session.add(user)
        db.session.commit()

        return redirect('/login')
    return render_template('register.html')

    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        form = request.form
        
        user = User.query.filter_by(username=form.get('username')).first()
        
        if(user):
            if(user.password ==  form.get('password')):
                session['username'] = user.username
                session['user_id'] = user.id
                return redirect('/')
            else:
                print('invalid password')
        else:
            print('username not found')
    return render_template('login.html')

@app.route('/sharedash')
def sharingDashboard():
    all_users = User.query.all()
    files = Encrypted.query.filter_by(user_id=session.get('user_id'))
    return render_template('share.html', all_users = all_users, files = files)

@app.route('/share')
def sharing():
    file_id = request.args.get('file_id')

    all_users = User.query.all()
    sel_file = Encrypted.query.filter_by(id=file_id).first()
    return render_template('sharefile.html', all_users = all_users, file = sel_file)

@app.route('/allow')
def allowuser():
    username = request.args.get('username')
    file_id = request.args.get('file_id')
    sel_file = Encrypted.query.filter_by(id=file_id).first()
    sel_file.allowed +=f'{username},'
    # db.session.update(sel_file)
    db.session.commit()
    return jsonify('success')

@app.route('/shared')
def allowedfiles():
    
    files = User.query.filter(User.allowed.contains(session.get("username")))
    print(files)
    
    return render_template('shared.html', files = files)

@app.route('/loader')
def loader():
    return render_template('loader.html')

@app.route('/')
def index():
    return render_template('homepage.html', username = session.get('username'))


@app.route('/encode')
def encode():
    return render_template('audio_encrypt.html')
        

@app.route('/decode')
def decode():
    return render_template('audio_decrypt.html')

@app.route('/uploadfile',methods=[ "GET",'POST'])
def uploadLabel():
    file=request.files.get('file')
    print(file)
    print(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
    return jsonify({'message' : 'success'})

@app.route('/encrypt',methods=["POST"])
def stegno_enc():
    msgs=request.form.get("message")
    print("msgs")
    sngs = request.files.get('file')
    enc_file = Encrypted(filename = sngs.filename, date = datetime.now(), allowed = '', user_id = session.get('user_id'))
    
    db.session.add(enc_file)
    db.session.commit()

    file_name = secure_filename(sngs.filename)
    
    if file_name.endswith('.mp3'):
        print(file_name) 
        os.system(f"""static/exe/ffmpeg -i /uploads/{file_name} -acodec pcm_u8 -ar 22050 /uploads/{file_name.replace('.mp3','.wav')}""")
        file_name = f'{file_name[:-4]}.wav'
    # filename=file_name[:file_name.rindex(".")]+" encrypted.wav"\
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
    if os.path.exists(filepath):
        sngs.save(filepath)
        print(filepath)
        file_data = Steganography().lsb(filepath,msgs)
        print("work done", file_name)
    else:
        print(filepath)
        print(os.listdir('uploads'))
        print('error finding wav file')
    return render_template("encrpy_success.html")

@app.route('/decrypt',methods=['POST'])
def stegno_dec():
    sngs = request.files.get('file')
    filename = secure_filename(sngs.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    sngs.save(filepath)
    print("till")
    decoded_msg=Steganaograpy_decryption().decoder(filepath)
    print("worked till here")
    print(decoded_msg)
    return render_template("decrpy_success.html",decoded_msg=decoded_msg)

@app.route("/return-file/")
def return_file():
    return send_file("outputs\song_emb.wav")

@app.route('/processes',methods=['POST'])
def process():
    song=request.form["file"]

    mesg=request.form["message"]

    if song and mesg:
        return jsonify({"success":" encryption"})

    else:
        return jsonify({'error':"Missing data"})
	

if __name__=="__main__":
    app.run(debug=True,threaded=True)

    
    
    

