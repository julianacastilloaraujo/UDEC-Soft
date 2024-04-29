from flask import Flask, render_template, request, redirect, url_for
from config import *
from miembroequipo import MiembroEquipo

con_bd = conexion()

app = Flask(__name__)

@app.route("/")
def index():
    coleccion=con_bd["MiembroEquipo"]
    MiembrosRegistrados = coleccion.find()
    return render_template('index.html', miembroequipo = MiembrosRegistrados)

@app.route('/guardar_miembroequipo', methods=['POST'])
def agregarMiembro():
    coleccion =con_bd["MiembroEquipo"]
    nombre =request.form['nombre']
    cargo =request.form['cargo']
    habilidades =request.form['habilidades']

    if nombre and cargo and habilidades:
        objmiembroequipo = MiembroEquipo(nombre,cargo,habilidades)
        coleccion.insert_one(objmiembroequipo.formato_doc())
        return redirect(url_for('index'))
                        
if __name__ == "__main__":
    app.run(debug=True)