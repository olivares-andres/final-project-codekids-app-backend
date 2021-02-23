from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique =True, nullable = False)
    username = db.Column(db.String(100), unique =True, nullable = False)
    password = db.Column(db.String(100), nullable= False)
    avatar = db.Column(db.String(100), nullable=True, default = 'default.png')
    type_user = db.Column(db.Integer)

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "avatar": self.avatar,
            "type_user":self.type_user
            #el type_user indicara si es usuario o profesor (1= usuario - 2= profesor)
        }

class News(db.Model):
    __tablename__= 'news'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique =True, nullable = False)

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email
        }
    

#Tabla Planeta 
class Planeta(db.Model):
    __tablename__ = "planeta"
    id = db.Column(db.Integer, primary_key=True)
    nombre_planeta = db.Column(db.String(100), nullable = False)
    misiones = db.relationship('Mision', backref='planeta')

    def serialize(self):
        return{
            "id": self.id,
            "nombre": self.nombre_planeta,
        }
    
    def serialize_with_mision(self):
        return{
            "id": self.id,
            "nombre": self.nombre_planeta,
            "mision": self.get_mision()
        }
    
    def get_mision(self):
        return list(map(lambda mision: mision.serialize(), self.mision))

    def save(self):
        db.session.add(self)
        db.session.commit()

#Tabla misión
class Mision(db.Model):
    __tablename__ = "mision"
    id = db.Column(db.Integer, primary_key=True)
    instrucciones = db.Column(db.Text(), nullable = False)
    codigo = db.Column(db.String(100), nullable = False)
    soluciones = db.Column(db.String(100), nullable = False)
    planeta_id = db.Column(db.Integer, db.ForeignKey('planeta.id'), nullable= False)

    def serialize(self):
        return{
            "id": self.id,
            "instrucciones": self.instrucciones,
            "codigo": self.codigo,
            "soluciones": self.soluciones,
            
        }
    
    def serialize_with_planet(self):
        return{
            "id": self.id,
            "instrucciones": self.instrucciones,
            "soluciones": self.soluciones,
            "codigo": self.codigo,
            "planeta_id": self.planeta_id
        }
    
    def save(self):
        db.session.add(self)
        db.session.commit()
