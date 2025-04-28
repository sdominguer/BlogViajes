from flask import Flask, render_template, request, redirect, url_for, flash, session
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


app = Flask(__name__)
app.config['SECRET_KEY'] = 'tu_clave_secreta'  # Cambia esto a una clave secreta adecuada
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'  # Archivo de la base de datos SQLite

app.config['UPLOAD_FOLDER'] = 'static/post_images'

# Config de los Emails
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'correo@gmail.com'  # Aquí tu correo
app.config['MAIL_PASSWORD'] = 'contra'  # Aquí tu contraseña.
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

db = SQLAlchemy(app)  # Se declara la base de datos
mail = Mail(app)  # Se declara Email
app.app_context().push()  # Se crea el entorno de la base de datos

# Modelos

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
    submit = SubmitField('Crear Post')

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
    return render_template('home.html', posts=posts)

@app.route('/about')
def about():
    return render_template('about.html')  # Renderiza el template about.html

@app.route('/work', methods=["GET", "POST"])
def work_with_me():
    form = ContactForm()
    if request.method == 'POST':
        if form.validate_on_submit:
            name = request.form['name']
            email = request.form['email']
            message = request.form['message']
            msg = Message("Hola, el usuario:" + name + " Te ha contactado: " + email, sender=email, recipients=['tuEmail@gmail.com'])  # Aquí tu correo
            msg.body = message
            mail.send(msg)
            flash('El formulario fue enviado con éxito')
            return redirect(url_for('index'))
    else:
        flash('El formulario tiene problemas, revisa los campos')
        return render_template('work_with_me.html', form=form)

    return render_template('work_with_me.html', form=form)

# Ruta para el login del administrador
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if 'admin_logged_in' in session:  # Si ya está logueado, redirige
        return redirect(url_for('create_post'))

    form = AdminLoginForm()
    if form.validate_on_submit():
        if form.password.data == 'tu_clave_admin':  # Aquí defines la clave de administrador
            session['admin_logged_in'] = True  # Guardamos el estado de login en la sesión
            flash('Has iniciado sesión correctamente', 'success')
            return redirect(url_for('create_post'))  # Redirige al formulario para crear post
        else:
            flash('Clave incorrecta. Intenta de nuevo.', 'danger')
            return redirect(url_for('admin_login'))

    return render_template('admin_login.html', form=form)

# Ruta para salir del login (cerrar sesión)
@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)  # Elimina el estado de sesión
    flash('Has cerrado sesión correctamente', 'info')
    return redirect(url_for('index'))  # Redirige al índice

# Ruta para crear un nuevo post
@app.route('/post/new', methods=['GET', 'POST'])
def create_post():
    if 'admin_logged_in' not in session:  # Verifica si el admin está logueado
        flash('Necesitas iniciar sesión para crear un post', 'danger')
        return redirect(url_for('admin_login'))

    form = PostForm()
    if form.validate_on_submit():
        picture_file = "default.jpg"  # Valor predeterminado si no se sube una imagen
        if form.image_file.data:
            picture_file = save_picture(form.image_file.data)

        post = Post(title=form.title.data, content=form.content.data, image_file=picture_file)
        
        # Procesar las recomendaciones
        num_recommendations = int(request.form.get('num_recommendations', 0))  # Obtener el número de recomendaciones desde el formulario
        for i in range(num_recommendations):
            recommendation_type = request.form.get(f'recommendation_type_{i}')
            comment = request.form.get(f'comment_{i}')
            rating = request.form.get(f'rating_{i}')
            contact = request.form.get(f'contact_{i}')
            price = request.form.get(f'price_{i}')
            
            recommendation = Recommendation(post=post, 
                                            recommendation_type=recommendation_type, 
                                            comment=comment, 
                                            rating=rating, 
                                            contact=contact, 
                                            price=price)
            db.session.add(recommendation)

        db.session.add(post)
        db.session.commit()
        flash('Post creado exitosamente', 'success')
        return redirect(url_for('index'))  # Redirige a la página principal

    return render_template('create_post.html', form=form, tipos_recomendacion=tipos_recomendacion)

# Ruta para editar un post
@app.route("/post/<int:post_id>/edit", methods=['GET', 'POST'])
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    form = PostForm()

    if form.validate_on_submit():
        # Actualizar los datos del post
        post.title = form.title.data
        post.content = form.content.data

        # Si se subió una nueva imagen
        if form.image_file.data:
            # Guardar la nueva imagen
            image_file = form.image_file.data
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(image_path)
            post.image_file = filename

        # Actualizar cada recomendación existente
        for idx, recommendation in enumerate(post.recommendations, start=1):
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

# Ruta para eliminar un post
@app.route('/post/<int:post_id>/delete', methods=['POST'])
def delete_post(post_id):
    if 'admin_logged_in' not in session:  # Verifica si el admin está logueado
        flash('Necesitas iniciar sesión para eliminar un post', 'danger')
        return redirect(url_for('admin_login'))

    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash('Post eliminado exitosamente', 'success')
    return redirect(url_for('index'))  # Redirige a la página principal

@app.route('/blog')
def blog():
    posts = Post.query.order_by(Post.date_posted.desc()).all()  # Obtiene todos los posts
    return render_template('blog.html', posts=posts)

@app.route('/post/<int:post_id>')
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)  # Obtiene el post por ID o retorna 404 si no existe
    return render_template('post_detail.html', post=post)


if __name__ == '__main__':
    app.run(debug=True)
