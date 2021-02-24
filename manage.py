import os
from flask import Flask, jsonify, request, render_template
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from models import db, User, News
from models import db, User, Planeta, Mision
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
from werkzeug.utils import secure_filename



BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static')
ALLOWED_IMAGES_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['DEBUG'] = 'True'
app.config['ENV'] = 'development'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'codekids.sqlite3')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = '465'
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_DEBUG'] = True
app.config['MAIL_USERNAME'] = '4geeks.server@gmail.com'
app.config['MAIL_PASSWORD'] = 'mpiiqyjxxfvwvofx'
JWTManager(app)
db.init_app(app)
mail = Mail(app)
bcrypt = Bcrypt(app)
Migrate(app, db)
CORS(app)

manager = Manager(app)
manager.add_command("db", MigrateCommand)

#funcion de extensiones permitidas
def allowed_images_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGES_EXTENSIONS

#funcion de enviar un mensaje
def send_mail(subject, sender, recipients, message):
    #estos son los campos del email
    msg = Message(subject,
                  sender=sender,
                  recipients=[recipients])
    #el contenido del mensaje a enviar
    msg.html = message
    #se envia finalmente el e-mail
    mail.send(msg)

@app.route('/')
def root():
    return render_template('index.html')

@app.route('/api/register', methods=['POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', None)
        password = request.form.get('password', None)
        
        if not username or username == '':
            return jsonify({"msg": "campo de username es obligatorio"})

        if not password or password == '':
            return jsonify({"msg": "campo de password es obligatorio"})
        
        #Vamos a validar que el usuario no exista previamente en la base de datos
        user = User.query.filter_by(username = username).first()
        
        #si existe un usuario entonces devolvemos mensaje de error
        if user:
            return jsonify({"msg": "Username existe"}), 400

        if 'avatar' in request.files:
            #AQUI CAPTURO EL ARCHIVO DE IMAGEN
            avatar = request.files['avatar']
            if avatar.filename != '':           
                if avatar and allowed_images_file(avatar.filename):
                    filename = secure_filename(avatar.filename)
                    avatar.save(os.path.join(os.path.join(app.config['UPLOAD_FOLDER'], 'img/avatars'), filename))
                else:
                    return jsonify({"msg": "tipo de imagen no permitida o extension incorrecta"})
        
        user = User()
        user.username = username
        #ahora vamos a usar Bcrypt para encriptar el password y no sea visible
        user.password = bcrypt.generate_password_hash(password)  
        user.type_user = 1      

        #validamos si el archivo de imagen avatar tiene algún nombre en caso contrario vamos a validar el nombre por defecto
        if 'avatar' in request.files:
            user.avatar = filename

        #aqui hacemos el insert a la db
        db.session.add(user)
        #aqui hacemos el commit para validar
        db.session.commit()

        #aqui le indicamos que le enviaremos al usuario al registrarse
        html = render_template('emails/email-register.html', user=user)

        send_mail("Registro", "4geeks.server@gmail.com", user.username, html)

        #generamos el token de accesso al usuario
        access_token = create_access_token(identity=user.username)
        #creamos un diccionario con los datos de acceso y los datos del usuario
        data = {
            "access_token": access_token,
            "user": user.serialize()
        }
        #retornamos todos los datos
        return jsonify(data), 200

@app.route('/api/login', methods=['POST'])
def login():
    if request.method == 'POST':
        #ahora validamos por un JSON
        username = request.json.get('username', None)
        password = request.json.get('password', None)
        
        if not username or username == '':
            return jsonify({"msg": "campo de username es obligatorio"})

        if not password or password == '':
            return jsonify({"msg": "campo de password es obligatorio"})
        
        #Vamos a validar que el usuario no exista previamente en la base de datos
        user = User.query.filter_by(username = username).first()
        
        #si NO existe un usuario entonces devolvemos mensaje de error
        if  not user:
            return jsonify({"msg": "Username no existe"}), 400
        
        #Validamos la contraseña a traves del hash encriptado si lo que ingresamos es igual entonces pasa 
        if bcrypt.check_password_hash(user.password, password):
            #generamos el token de accesso al usuario
            access_token = create_access_token(identity=user.username)
            #creamos un diccionario con los datos de acceso y los datos del usuario
            data = {
                "access_token": access_token,
                "user": user.serialize()
            }
            #retornamos todos los datos
            return jsonify(data), 200
        else:
            return jsonify({"msg": "nombre de usuario o contraseña incorrecta, verifique sus datos"}), 401

@app.route('/api/news', methods=['POST', 'GET'])
def news(id = None):
    if request.method == 'GET':
        if id is not None:
            news = News.query.get(id)
            if not news: return jsonify({"msg": "bad request"}), 404
            return jsonify(news.serialize()), 200
        else:
            news_all = News.query.all()
            news_all = list(map(lambda news: news.serialize(), news_all))
            return jsonify(news_all), 200
    if request.method == 'POST':
        email = request.json.get("email")

    news = News()
    news.email = email

    db.session.add(news)
    db.session.commit()

    return jsonify({"msg":"ok"}), 200
    
@app.route('/api/planetas', methods=['GET', 'POST'])
@app.route('/api/planeta/<int:id>', methods=['GET', 'POST'])
def planetas(id = None):
    if request.method == 'GET':
        if id is not None:
            planeta = Planeta.query.get(id)
            if not planeta: return jsonify({"msg": "planeta no existe"}), 404
            return jsonify(planeta.serialize()),200
        else:
            planetas = Planeta.query.all()
            planetas = list(map(lambda planeta : planeta.serialize(), planetas))
            return jsonify(planetas),200

    if request.method == 'POST':
        nombre_planeta = request.json.get('nombre_planeta')
    
    if not nombre_planeta: return jsonify({"msg": "nombre de planeta requerido"})

    planeta = Planeta()
    planeta.nombre_planeta = nombre_planeta
    #aqui hacemos el insert a la db
    db.session.add(planeta)
        #aqui hacemos el commit para validar
    db.session.commit()

    return jsonify(planeta.serialize()), 201



@app.route('/api/planeta/<int:planeta_id>/mision', methods=['GET'])
@app.route('/api/planeta/<int:planeta_id>/mision/<int:id>', methods=['GET'])
def planeta_with_mision(planeta_id, id = None): 
    if request.method == 'GET':
        if id is not None:
            mision = Mision.query.filter_by(planeta_id = planeta_id, id =id).first()
            if not mision: return jsonify({"msg": "Mision no encontrada"}), 404
            return jsonify(mision.serialize()), 200
        else:
            misiones = Mision.query.filter_by(planeta_id=planeta_id)
            misiones = list(map(lambda mision: mision.serialize(), misiones))
            return jsonify(misiones),200



@app.route('/api/misiones', methods=['GET', 'POST'])
@app.route('/api/mision/<int:id>', methods=['GET', 'PUT'])
def misiones(id = None):
    if request.method == 'GET':
        if id is not None:
            mision = Mision.query.get(id)
            if not mision: return jsonify({"msg": "mision no existe"}), 404
            return jsonify(mision.serialize()),200
        else:
            misiones = Mision.query.all()
            misiones = list(map(lambda mision : mision.serialize_with_planet(), misiones))
            return jsonify(misiones), 200

    if request.method == 'POST':
        instrucciones = request.json.get("instrucciones")
        codigo = request.json.get("codigo")
        soluciones = request.json.get("soluciones")
        planeta_id = request.json.get("planeta_id")

        mision = Mision()
        mision.instrucciones = instrucciones
        mision.soluciones = soluciones
        mision.codigo = codigo
        mision.planeta_id = planeta_id 
       
       #aqui hacemos el insert a la db
        db.session.add(mision)
        #aqui hacemos el commit para validar
        db.session.commit()

        return jsonify(mision.serialize_with_planet()),201

    

#para crear la base de datos usar los siguientes comandos:
# python manage.py db init
# python manage.py db migrate
# python manage.py db upgrade

if __name__ == '__main__':
    manager.run()


