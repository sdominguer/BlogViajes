from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, FileField, IntegerField, SelectField
from wtforms.validators import DataRequired, NumberRange, URL
from flask_wtf.file import FileField, FileAllowed
import os
import secrets
from flask_mail import Mail, Message  # Se Importan
from sqlalchemy.orm import relationship

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tu_clave_secreta'  # ¡Cambia esto!
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'  # Archivo de la base de datos SQLite

# Config de los Emails
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'correo@gmail.com'  # Aqui tu correo
app.config['MAIL_PASSWORD'] = 'contra'  # Aqui tu contraseña.

app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
db = SQLAlchemy(app)  # Se declara la base de datos
mail = Mail(app)  # Se declara Email
app.app_context().push()  # Se crea el entorno de la base de datos

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

# Lista con los tipos de recomendación
tipos_recomendacion = [
    ('Hotel', 'Hotel'),
    ('Restaurante', 'Restaurante'),
    ('Lugar', 'Lugar'),
    ('Actividad', 'Actividad'),
    ('Otro', 'Otro')
]

class PostForm(FlaskForm):
    title = StringField('Título', validators=[DataRequired()])
    content = TextAreaField('Contenido', validators=[DataRequired()])
    image_file = FileField('Imagen del Post', validators=[FileAllowed(['jpg', 'jpeg', 'png'])])
    submit = SubmitField('Crear Post')

    def validate_image_file(form, field):
        if field.data:
            if field.data.filename.rsplit('.', 1)[1].lower() not in ['jpg', 'jpeg', 'png']:
                raise ValidationError('Formato de imagen no válido. Solo se permiten archivos JPG, JPEG y PNG.')

# Aqui se crea el formulario
class ContactForm(FlaskForm):
    name = StringField("Nombre:", validators=[DataRequired()])
    email = StringField("Email:", validators=[DataRequired()])
    message = TextAreaField("Mensaje:", validators=[DataRequired()])
    submit = SubmitField("Enviar")

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/post_images', picture_fn)
    form_picture.save(picture_path)

    return picture_fn

@app.route('/')
def index():
    posts = Post.query.order_by(Post.date_posted.desc()).limit(6).all()
    return render_template('home.html', posts=posts)

@app.route('/about')
def about():
    return render_template('about.html')  # Renderiza el template about.html

@app.route('/work',  methods = ["GET", "POST"])
def work_with_me():
    form = ContactForm()

    if request.method == 'POST':
          if form.validate_on_submit:
            name = request.form['name']
            email = request.form['email']
            message = request.form['message']
            msg = Message("Hola, el usuario:" +  name + " Te ha contactado: " + email, sender = email, recipients = ['tuEmail@gmail.com'])#Aqui tu correo
            msg.body = message
            mail.send(msg)
            flash('El formulario fue enviado con exito')
            return redirect(url_for('index'))
    else:
            flash('El formulario tiene problemas, revisa los campos')
            return render_template('work_with_me.html', form=form)

    return render_template('work_with_me.html', form=form)

@app.route('/post/new', methods=['GET', 'POST'])
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        picture_file = "default.jpg"  # Valor predeterminado
        if form.image_file.data:
            picture_file = save_picture(form.image_file.data)
        post = Post(title=form.title.data, content=form.content.data, image_file=picture_file)

        # Obtener las recomendaciones del formulario
        num_recommendations = int(request.form.get('num_recommendations', 0))  # Obtener la cantidad de recomendaciones
        for i in range(num_recommendations):
            recommendation_type = request.form.get(f'recommendation_type_{i}')
            comment = request.form.get(f'comment_{i}')
            rating = request.form.get(f'rating_{i}')
            contact = request.form.get(f'contact_{i}')
            price = request.form.get(f'price_{i}')  # Obtener el precio

            recommendation = Recommendation(post=post, recommendation_type=recommendation_type, comment=comment, rating=rating, contact=contact, price=price)
            db.session.add(recommendation)

        db.session.add(post)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('create_post.html', form=form, tipos_recomendacion=tipos_recomendacion)

@app.route('/blog')
def blog():
    posts = Post.query.order_by(Post.date_posted.desc()).all()
    return render_template('blog.html', posts=posts)

if __name__ == '__main__':
    app.run(debug=True)