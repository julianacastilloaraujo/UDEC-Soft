from flask import Flask, render_template, request, redirect, url_for,flash,session,json
from config import *

app = Flask(__name__)
app.secret_key = 'key233212'

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/iniciarSesion", methods=['GET', 'POST'])
def iniciarSesion():
    if request.method == 'POST':
        email = request.form['correo']
        password = request.form['password']
        id_token = iniciar_sesion(email, password)
        session['id_token'] = id_token
        if id_token:
            flash('Inicio de sesión exitoso')
            return redirect(url_for('lobbyProjects'))  # Cambia 'inicio' por la ruta de tu página de inicio
        else:
            flash('Error en el inicio de sesión')
            return redirect(url_for('iniciarSesion'))
    
    return render_template('iniciarSesion.html')

@app.route("/registrarse" , methods=['GET', 'POST'])
def registrarse():
    if request.method == 'POST':
        email = request.form['usuarioCorreo']
        contraseña = request.form['contrasena']
        contraseña_confirm = request.form['contrasenaConfirm']
        rol = request.form['rol']

        if contraseña != contraseña_confirm:
            flash('Las contraseñas no coinciden.')
            return redirect(url_for('registrarse'))


        resultado = registrar_usuario(email, contraseña, rol)
        flash(resultado)
        return redirect(url_for('registrarse'))
    
    return render_template('registrarse.html')

@app.route("/createProjects", methods=['GET', 'POST'])
def createProjects():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        fecha_inicio = request.form.get('fecha_inicio')
        estado = request.form.get('estado')
        fecha_fin = request.form.get('fecha_fin')
        descripcion = request.form.get('descripcion')
         # Obtener y analizar los miembros como lista desde el JSON
        miembros_json = request.form.get('miembros_json')
        miembros = json.loads(miembros_json) if miembros_json else []
        # Obtener el token del usuario autenticado (esto debe manejarse con sesiones o autenticación adecuada)
        id_token = session.get('id_token')
        
        if id_token:
            uid = obtener_uid_usuario_actual(id_token)
            if uid:
                # Crear la lista de usuarios con el UID del usuario actual
                lista_usuarios = [uid]
                resultado = crear_Proyecto(uid, nombre, descripcion, lista_usuarios, fecha_inicio, fecha_fin, estado,miembros)
                return redirect(url_for('lobbyProjects'))
            else:
                return "Error: No se pudo obtener el UID del usuario actual"
        else:
            return "Error: Usuario no autenticado"
    return render_template('createProjects.html')

@app.route("/tareas/<project_id>")
def tareas(project_id):
    # Obtener el id_token de la sesión y el UID del usuario actual
    id_token = session.get('id_token')
    if not id_token:
        return "Error: Usuario no autenticado"
    
    uid = obtener_uid_usuario_actual(id_token)
    if not uid:
        return "Error: No se pudo obtener el UID del usuario actual"
    
    # Obtener las tareas del proyecto desde la base de datos
    tareas = obtener_tareas(uid, project_id)
    if tareas is None:
        return "Error: No se pudieron obtener las tareas"

    # Renderizar la plantilla con las tareas obtenidas
    return render_template('tareas.html', project_id=project_id, tareas=tareas)

       
@app.route("/createTasks/<project_id>", methods=['GET', 'POST'])
def createTasks(project_id):
    if request.method == 'POST':
        if 'titulo' in request.form and 'descripcion' in request.form and 'fecha' in request.form and 'estado' in request.form:
            titulo = request.form['titulo']
            descripcion = request.form['descripcion']
            fecha = request.form['fecha']
            estado = request.form['estado']
            task_data = {
                'titulo': titulo,
                'descripcion': descripcion,
                'estado': estado,
                'fecha': fecha
            }
            id_token = session.get('id_token')  
            if id_token:
                uid = obtener_uid_usuario_actual(id_token)
                if uid:
                    # Crear la lista de usuarios con el UID del usuario actual
                    resultado = crear_tarea(uid, project_id, task_data)
                    return redirect(url_for('lobbyProjects'))
                else:
                    return "Error: No se pudo obtener el UID del usuario actual"
            else:
                return "Error: Usuario no autenticado"
        else:
            # Si falta algún campo en el formulario, puedes mostrar un mensaje de error al usuario
            error_message = "Por favor, completa todos los campos del formulario."
            return render_template('createTasks.html', project_id=project_id, error_message=error_message)
    else:
        # Si la solicitud no es POST, simplemente renderiza el formulario vacío
        return render_template('createTasks.html', project_id=project_id)


@app.route("/lobbyProjects")
def lobbyProjects():
    id_token = session.get('id_token')
    if id_token:
        uid = obtener_uid_usuario_actual(id_token)
        if uid:
            proyectos = obtener_proyectos(uid)
            return render_template('lobbyProjects.html', proyectos=proyectos)
        else:
            return "Error: No se pudo obtener el UID del usuario actual"
    else:
        return "Error: Usuario no autenticado"
    
@app.route("/updateProjects/<project_id>", methods=['GET', 'POST'])
def updateProjects(project_id):
    id_token = session.get('id_token')
    if not id_token:
        return "Error: Usuario no autenticado"

    uid = obtener_uid_usuario_actual(id_token)
    if not uid:
        return "Error: No se pudo obtener el UID del usuario actual"

    if request.method == 'POST':
        titulo = request.form.get('titulo')
        descripcion = request.form.get('descripcion')
        fechaInicio = request.form.get('fechaInicio')
        fechaFin = request.form.get('fechaFin')
        estado = request.form.get('estado')
        miembros = request.form.get('miembros').split(',')

        # Llamar a la función para actualizar el proyecto
        actualizar_proyecto(uid, project_id, titulo, descripcion, fechaInicio, fechaFin, estado, miembros)
        return redirect(url_for('lobbyProjects'))

    project = obtener_proyecto_por_id(uid, project_id)
    if 'miembros' not in project or project['miembros'] is None:
        project['miembros'] = []

    # Convertir la lista de miembros a una cadena separada por comas
    miembros_str = ','.join(project['miembros'])
    return render_template('updateProjects.html', project=project, project_id=project_id, miembros_str=miembros_str)




@app.route("/deleteProject/<project_id>", methods=['GET', 'POST'])
def deleteProject(project_id):
    id_token = session.get('id_token')
    if not id_token:
        return "Error: Usuario no autenticado"
    
    uid = obtener_uid_usuario_actual(id_token)
    if not uid:
        return "Error: No se pudo obtener el UID del usuario actual"
    
    try:
        db.collection('usuario').document(uid).collection('proyectos').document(project_id).delete()
        print(f"Proyecto {project_id} eliminado correctamente")
    except Exception as e:
        print(f"Error al eliminar el proyecto: {e}")
    
    return redirect(url_for('lobbyProjects'))

@app.route('/guardar_miembroequipo', methods=['POST'])
def agregarMiembro():
    nombre =request.form['nombre']
    cargo =request.form['cargo']
    habilidades =request.form['habilidades']

        
                        
if __name__ == "__main__":
    app.run(debug=True)