import datetime as dt
import jwt
from flask import current_app
from flaskblog import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)

    def get_reset_token(self, expires_sec=1800):
        # s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        # return s.dumps({'user_id': self.id}).decode('utf-8')
        reset_token = jwt.encode({
            'user_id': self.id,
            'exp': dt.datetime.utcnow() + dt.timedelta(seconds=expires_sec)
        }, current_app.config['SECRET_KEY'], algorithm="HS256")
        return reset_token

    @staticmethod
    def verify_reset_token(token):
        # s = Serializer(current_app.config['SECRET_KEY'])
        # try:
        #     user_id = s.loads(token)['user_id']
        # except:
        #     return None
        try:
            data = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                leeway=dt.timedelta(seconds=10),
                algorithms=["HS256"],
            )
            user_id = data.get('user_id')
        except:
            return None
        
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

    def get_profile_picture_url(self):
        return f"https://{current_app.config['AWS_BUCKET_NAME']}.s3.{current_app.config['AWS_DEFAULT_REGION']}.amazonaws.com/static/profile_pics/{self.image_file}"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"
