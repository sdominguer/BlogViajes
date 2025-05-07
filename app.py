from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, PasswordField, FileField
from wtforms.validators import DataRequired, Email, EqualTo
from flask_wtf.file import FileAllowed
import os
import secrets
from flask_mail import Mail, Message
from sqlalchemy.orm import relationship
from werkzeug.utils import secure_filename
import smtplib
from email.mime.text import MIMEText


app = Flask(__name__)
app.config['SECRET_KEY'] = 'tu_clave_secreta'  # Cambia esto a una clave secreta adecuada
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'  # Archivo de la base de datos SQLite

app.config['UPLOAD_FOLDER'] = 'static/post_images'

# Configuración de Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'anasofiacasrpo@gmail.com'         # PON AQUÍ TU CORREO
app.config['MAIL_PASSWORD'] = 'zbqu xmyg orsq wlrd' # CONTRASEÑA DE APP, no tu password normal
app.config['MAIL_DEFAULT_SENDER'] = 'anasofiacasrpo@gmail.com'

mail = Mail(app)

db = SQLAlchemy(app)  # Se declara la base de datos
mail = Mail(app)  # Se declara Email
app.app_context().push()  # Se crea el entorno de la base de datos

# Modelos

class Subscriber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')  # Nuevo campo
    recommendations = relationship("Recommendation", back_populates="post", cascade="all, delete-orphan")

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"


class Recommendation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    recommendation_type = db.Column(db.String(50), nullable=True)
    comment = db.Column(db.Text, nullable=True)
    rating = db.Column(db.Integer, nullable=True)
    contact = db.Column(db.String(100), nullable=True)
    price = db.Column(db.String(50), nullable=True)
    post = relationship("Post", back_populates="recommendations")

    def __repr__(self):
        return f"Recommendation('{self.recommendation_type}', '{self.comment}')"

# Lista de tipos de recomendación
tipos_recomendacion = [
    ('Hotel', 'Hotel'),
    ('Excursion', 'Excursión'),
    ('Restaurante', 'Restaurante'),
    ('Lugar', 'Lugar'),
    ('Persona', 'Persona')
]

# Formulario de login para el administrador
class AdminLoginForm(FlaskForm):
    password = PasswordField('Clave de acceso', validators=[DataRequired()])
    submit = SubmitField('Entrar')

# Formulario de creación de post
class PostForm(FlaskForm):
    title = StringField('Título', validators=[DataRequired()])
    content = TextAreaField('Contenido', validators=[DataRequired()])
    image_file = FileField('Imagen del Post', validators=[FileAllowed(['jpg', 'jpeg', 'png'])])
    submit = SubmitField('Guardar Post')

# Función para guardar imágenes
def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/post_images', picture_fn)
    form_picture.save(picture_path)
    return picture_fn

# Rutas existentes que tienes

@app.route('/')
def index():
    posts = Post.query.order_by(Post.date_posted.desc()).limit(6).all()

    galeria_root = os.path.join(app.static_folder, 'galeria')
    paises = []

    for pais in os.listdir(galeria_root):
        path_pais = os.path.join(galeria_root, pais)
        if os.path.isdir(path_pais):
            imagenes = sorted([img for img in os.listdir(path_pais) if img.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))])
            if imagenes:
                paises.append({
                    'nombre': pais,
                    'imagen_destacada': f'galeria/{pais}/{imagenes[0]}'
                })

    return render_template('home.html', posts=posts, paises=paises)

@app.route('/about')
def about():
    return render_template('about.html')  # Renderiza el template about.html

# Ruta para suscripción
@app.route('/subscribe', methods=['POST'])
def subscribe():
    email = request.form['email']
    if Subscriber.query.filter_by(email=email).first():
        flash('You are already subscribed.', 'info')
    else:
        new_subscriber = Subscriber(email=email)
        db.session.add(new_subscriber)
        db.session.commit()
        flash('Thanks for subscribing!', 'success')
    return redirect('/')

# Función para enviar correos
def send_email(to, subject, body):
    sender = 'tucorreo@gmail.com'
    password = 'tu_contraseña_de_aplicacion'
    
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = to

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(sender, password)
        smtp.send_message(msg)

@app.route('/galeria/<pais>')
def galeria_pais(pais):
    path_pais = os.path.join(app.static_folder, 'galeria', pais)
    if not os.path.isdir(path_pais):
        abort(404)

    imagenes = sorted([
        f'galeria/{pais}/{img}' for img in os.listdir(path_pais)
        if img.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))
    ])

    return render_template('galeria_pais.html', pais=pais, imagenes=imagenes)


# Ruta para la página "Work with Me"
@app.route('/work_with_me', methods=['GET'])
def work_with_me():
    return render_template('work_with_me.html')  # Solo muestra la página, no es necesario manejar formularios aquí

# Ruta para la página de Contacto
@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        
        # Crear el mensaje
        msg = Message('Nuevo mensaje de colaboración',
                      recipients=['anasofiacasrpo@gmail.com'])  # A dónde quieres recibir el mensaje
        msg.body = f"Nombre: {name}\nCorreo: {email}\nMensaje:\n{message}"
        
        try:
            # Enviar el mensaje
            mail.send(msg)
            flash('Tu mensaje ha sido enviado con éxito', 'success')
            return redirect(url_for('contact'))  # Redirige de vuelta al formulario de contacto con un mensaje de éxito
        except Exception as e:
            print(str(e))
            flash('Error al enviar el mensaje. Intenta de nuevo más tarde.', 'danger')
    
    return render_template("contact.html")

# Ruta para el login del administrador
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if 'admin_logged_in' in session:  # Si ya está logueado, redirige
        return redirect(url_for('create_post'))

    form = AdminLoginForm()
    next_page = request.args.get('next', '')  # Obtener la página a la que redirigir después del login

    if form.validate_on_submit():
        if form.password.data == 'tu_clave_admin':  # Aquí defines la clave de administrador
            session['admin_logged_in'] = True  # Guardamos el estado de login en la sesión
            flash('Has iniciado sesión correctamente', 'success')
            
            # Redirigir a la página solicitada o a crear post si no hay redirección
            if next_page:
                return redirect(next_page)
            return redirect(url_for('create_post'))
        else:
            flash('Clave incorrecta. Intenta de nuevo.', 'danger')
            return redirect(url_for('admin_login', next=next_page))

    return render_template('admin_login.html', form=form, next_page=next_page)

# Ruta para salir del login (cerrar sesión)
@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)  # Elimina el estado de sesión
    flash('Has cerrado sesión correctamente', 'info')
    return redirect(url_for('index'))  # Redirige al índice



#Ruta para crear un nuevo post

from flask_mail import Message

@app.route('/post/new', methods=['GET', 'POST'])
def create_post():
    if 'admin_logged_in' not in session:
        flash('Necesitas iniciar sesión para crear un post', 'danger')
        return redirect(url_for('admin_login', next=url_for('create_post')))

    form = PostForm()
    if form.validate_on_submit():
        picture_file = "default.jpg"
        if form.image_file.data:
            picture_file = save_picture(form.image_file.data)

        post = Post(title=form.title.data, content=form.content.data, image_file=picture_file)

        num_recommendations = int(request.form.get('num_recommendations', 0))
        for i in range(num_recommendations):
            recommendation_type = request.form.get(f'recommendation_type_{i}')
            comment = request.form.get(f'comment_{i}')
            rating = request.form.get(f'rating_{i}')
            contact = request.form.get(f'contact_{i}')
            price = request.form.get(f'price_{i}')

            recommendation = Recommendation(
                post=post,
                recommendation_type=recommendation_type,
                comment=comment,
                rating=rating,
                contact=contact,
                price=price
            )
            db.session.add(recommendation)

        db.session.add(post)
        db.session.commit()

        # Enviar correos a los suscriptores
        subject = "¡Nuevo post en Trail & Tales!"
        body = f"""
Hola viajero/a 👋

¡Un nuevo post ha sido publicado en Trail & Tales! 🌍

📌 Título: {post.title}

✨ Descubre las últimas recomendaciones de viaje, secretos de ruta y tips para tu próxima aventura.

Puedes leerlo aquí:
👉 http://localhost:5000/blog  (actualízalo con tu dominio real cuando publiques)

Gracias por ser parte de esta comunidad viajera 💌

Con cariño,
Ana Sofía 🌸
"""

        # Obtener todos los suscriptores
        subscribers = Subscriber.query.all()
        for subscriber in subscribers:
            try:
                msg = Message(subject, recipients=[subscriber.email], body=body)
                mail.send(msg)
            except Exception as e:
                print(f"Error al enviar correo a {subscriber.email}: {e}")

        flash('Post creado exitosamente', 'success')
        return redirect(url_for('index'))

    return render_template('create_post.html', form=form, tipos_recomendacion=tipos_recomendacion)


# Ruta para editar un post - ahora con protección de contraseña
@app.route("/post/<int:post_id>/edit", methods=['GET', 'POST'])
def edit_post(post_id):
    # Verifica si el usuario está logueado como administrador
    if 'admin_logged_in' not in session:
        flash('Necesitas iniciar sesión para editar un post', 'danger')
        return redirect(url_for('admin_login', next=url_for('edit_post', post_id=post_id)))
    
    post = Post.query.get_or_404(post_id)
    form = PostForm()

    if form.validate_on_submit():
        # Actualizar los datos del post
        post.title = form.title.data
        post.content = form.content.data

        # Si se subió una nueva imagen
        if form.image_file.data:
            # Guardar la nueva imagen
            picture_file = save_picture(form.image_file.data)
            post.image_file = picture_file

        # Actualizar cada recomendación existente
        for idx, recommendation in enumerate(post.recommendations, start=0):
            recommendation.recommendation_type = request.form.get(f'recommendation_type_{idx}')
            recommendation.comment = request.form.get(f'comment_{idx}')
            recommendation.rating = int(request.form.get(f'rating_{idx}', 1))
            recommendation.contact = request.form.get(f'contact_{idx}')
            recommendation.price = request.form.get(f'price_{idx}')

        # Añadir nueva recomendación si hay datos
        if request.form.get('comment_new') and request.form.get('rating_new'):
            new_recommendation = Recommendation(
                recommendation_type=request.form.get('recommendation_type_new'),
                comment=request.form.get('comment_new'),
                rating=int(request.form.get('rating_new')),
                contact=request.form.get('contact_new'),
                price=request.form.get('price_new'),
                post=post
            )
            db.session.add(new_recommendation)

        db.session.commit()
        flash('El post fue actualizado exitosamente.', 'success')
        return redirect(url_for('post_detail', post_id=post.id))

    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content

    return render_template('edit_post.html', form=form, post=post)

@app.route('/post/delete/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    if 'admin_logged_in' not in session:
        flash('Necesitas iniciar sesión para eliminar un post', 'danger')
        return redirect(url_for('admin_login', next=url_for('post_detail', post_id=post_id)))

    post = Post.query.get_or_404(post_id)

    db.session.delete(post)
    db.session.commit()
    flash('El post ha sido eliminado correctamente.', 'success')
    return redirect(url_for('blog'))  # Redirige a la página de blog

@app.route('/blog')
def blog():
    posts = Post.query.order_by(Post.date_posted.desc()).all()  # Obtiene todos los posts
    return render_template('blog.html', posts=posts)

@app.route('/post/<int:post_id>')
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)  # Obtiene el post por ID o retorna 404 si no existe
    return render_template('post_detail.html', post=post)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)