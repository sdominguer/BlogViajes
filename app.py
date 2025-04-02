from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('home.html')  # Renderiza home.html en lugar de index.html

if __name__ == '__main__':
    app.run(debug=True)