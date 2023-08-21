from flask import Flask, render_template, request, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
import boto3, uuid, os

os.environ['AWS_PROFILE'] = 'public-django-s3-user'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg'}

def allowed_file(filename):
  return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

db = SQLAlchemy()

class File(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  original_filename = db.Column(db.String(100))
  filename = db.Column(db.String(100))
  bucket = db.Column(db.String(100))
  region = db.Column(db.String(100))

def create_app():
  app = Flask(__name__)
  app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///s3example.db"
  app.config['SECRET_KEY'] = 'thisisasecret'

  db.init_app(app)

  @app.route("/", methods=['GET', 'POST'])
  def index():
    if request.method == 'POST':
      uploaded_file = request.files['file-to-save']
      if not allowed_file(uploaded_file.filename):
        flash('File not allowed', 'red')
        return redirect(url_for('index'))
      
      bucket_name = "flask-s3-public"
      new_filename = uuid.uuid4().hex + '.' + uploaded_file.filename.rsplit('.', 1)[1].lower()
      
      s3 = boto3.resource("s3")
      s3.Bucket(bucket_name).upload_fileobj(uploaded_file, new_filename)

      file = File(
        original_filename = uploaded_file.filename,
        filename = new_filename,
        bucket = bucket_name,
        region = 'us-east-2',
      )
      db.session.add(file)
      db.session.commit()
      flash('OK File Uploaded', 'green')
      return redirect(url_for('index'))
    
    files = File.query.all()
    return render_template("index.html", files=files, extensions=', '.join(ALLOWED_EXTENSIONS))

  return app
