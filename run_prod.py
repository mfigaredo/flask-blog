import os
# from dotenv import load_dotenv
# load_dotenv()

from flaskblog import create_app, db

app = create_app()

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0", port=os.getenv('PORT', default=5000))
