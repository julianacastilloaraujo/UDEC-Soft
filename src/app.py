from flask import Flask, render_template, request, redirect, url_for
from config import *

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/iniciarSesion", methods=['GET','POST'])
def iniciarSesion():
    return render_template('iniciarSesion.html')

@app.route("/registrarse")
def registrarse():
    return render_template('registrarse.html')

@app.route('/guardar_miembroequipo', methods=['POST'])
def agregarMiembro():
    nombre =request.form['nombre']
    cargo =request.form['cargo']
    habilidades =request.form['habilidades']

    if nombre and cargo and habilidades:
        return redirect(url_for('index'))
                        
if __name__ == "__main__":
    app.run(debug=True)