from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, FileField
from wtforms.validators import DataRequired, ValidationError
from flask_wtf.file import FileField, FileAllowed
import os
import secrets

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tu_clave_secreta'  # ¡Cambia esto!
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'  # Archivo de la base de datos SQLite
db = SQLAlchemy(app) #Se declara la base de datos
app.app_context().push() #Se crea el entorno de la base de datos

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')  # Nuevo campo

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"
    

class PostForm(FlaskForm):
    title = StringField('Título', validators=[DataRequired()])
    content = TextAreaField('Contenido', validators=[DataRequired()])
    image_file = FileField('Imagen del Post', validators=[FileAllowed(['jpg', 'jpeg', 'png'])])  # Nuevo campo
    submit = SubmitField('Crear Post')

    def validate_image_file(form, field):
        if field.data:
            if field.data.filename.rsplit('.', 1)[1].lower() not in ['jpg', 'jpeg', 'png']:
                raise ValidationError('Formato de imagen no válido. Solo se permiten archivos JPG, JPEG y PNG.')


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

@app.route('/post/new', methods=['GET', 'POST'])
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        if form.image_file.data:
            picture_file = save_picture(form.image_file.data)
        else:
            picture_file = "default.jpg"
        post = Post(title=form.title.data, content=form.content.data, image_file=picture_file)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('create_post.html', form=form)

@app.route('/blog')
def blog():
    posts = Post.query.order_by(Post.date_posted.desc()).all()
    return render_template('blog.html', posts=posts)

if __name__ == '__main__':
    app.run(debug=True)