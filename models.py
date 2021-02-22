from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique =True, nullable = False)
    password = db.Column(db.String(100), nullable= False)
    avatar = db.Column(db.String(100), nullable=True, default = 'default.png')

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "avatar": self.avatar
        }

    