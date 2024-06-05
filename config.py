import firebase_admin
from firebase_admin import credentials, firestore, auth,storage
import requests

# Inicializa Firestore DB
firebase_sdk = credentials.Certificate('src/udecsoft-8be27-firebase-adminsdk-wpz3v-9650bee75f.json')
firebase_admin.initialize_app(firebase_sdk, {
    'storageBucket': 'gs://udecsoft-8be27.appspot.com'
})
db = firestore.client()

def obtener_uid_usuario_actual(id_token):
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token['uid']
    except Exception as e:
        print(f"Error al obtener UID del usuario actual: {e}")
        return None
    
def registrar_usuario(email, contraseña, rol):
    try:
        usuario_existente = auth.get_user_by_email(email)
        return 'El usuario ya está registrado'
    except firebase_admin.auth.UserNotFoundError:
        try:
            usuario = auth.create_user(
                email=email,
                password=contraseña
            )
            datos_usuario = {
                'Correo': email,
                'rol': rol
            }
            db.collection('usuario').document(usuario.uid).set(datos_usuario)
            return 'Usuario registrado exitosamente'
        except Exception as e:
            return f'Ocurrió un error: {str(e)}'
    except Exception as e:
        return f'Ocurrió un error al verificar el usuario: {str(e)}'

def iniciar_sesion(email, contraseña):
    try:
        firebase_auth_url = 'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword'
        api_key = 'AIzaSyByJUbyvL6Jv0eCtj9Lb9QS2ZgMck6qvVg'
        payload = {
            'email': email,
            'password': contraseña,
            'returnSecureToken': True
        }
        response = requests.post(firebase_auth_url, params={'key': api_key}, json=payload)
        response_data = response.json()

        if response.status_code == 200:
            id_token = response_data['idToken']
            print('Inicio de sesión exitoso')
            return id_token
        else:
            error_message = response_data['error']['message']
            print('Error en el inicio de sesión:', error_message)
            return None
    except Exception as e:
        print('Ocurrió un error:', str(e))
        return None

def obtener_usuarios():
    try:
        users_ref = db.collection('usuario')
        users = users_ref.stream()
        user_list = []
        for user in users:
            user_data = user.to_dict()
            user_data['id'] = user.id  
            user_data['correo'] = user_data.pop('Correo')  
            user_data['rol'] = user_data.pop('rol')  
            user_list.append(user_data)
        return user_list
    except Exception as e:
        return None

def crear_Proyecto(uid, titulo, descripcion, lista_usuarios,fecha_inicio, fecha_fin , estado,miembros):
    try:
        proyecto_data = {
            'titulo': titulo,
            'descripcion': descripcion,
            'usuarios': lista_usuarios,
            'fechaInicio':fecha_inicio,
            'fechaFin': fecha_fin,
            'estado':estado,
            'miembros':miembros
        }
        db.collection('usuario').document(uid).collection('proyectos').add(proyecto_data)
        return 'Proyecto creado exitosamente'
    except Exception as e:
        print(f"Error al enviar proyecto a la base de datos: {e}")
        return f"Error: {e}"
    

def obtener_proyectos(uid):
    try:
        usuariosAuth_ref = db.collection('usuario').document(uid).collection('proyectos')
        actividades = usuariosAuth_ref.get()
        lista_proyectos = []
        for actividad in actividades:
            actividad_data = actividad.to_dict()
            actividad_data['id'] = actividad.id 
            actividad_data['titulo'] = actividad_data.pop('titulo')  
            actividad_data['descripcion'] = actividad_data.pop('descripcion')  
            actividad_data['usuarios'] = actividad_data.pop('usuarios')  
            actividad_data['fechaInicio'] = actividad_data.pop('fechaInicio') 
            actividad_data['fechaFin'] = actividad_data.pop('fechaFin')
            actividad_data['estado'] = actividad_data.pop('estado')
            lista_proyectos.append(actividad_data)
        return lista_proyectos
    except Exception as e:
        print(f"Error al obtener las actividades: {e}")
        return []


def actualizar_proyecto(uid, project_id, titulo, descripcion, fechaInicio, fechaFin, estado,miembros):
    try:
        proyecto_ref = db.collection('usuario').document(uid).collection('proyectos').document(project_id)
        proyecto_ref.update({
            'titulo': titulo,
            'descripcion': descripcion,
            'fechaInicio': fechaInicio,
            'fechaFin': fechaFin,
            'estado': estado,
            'miembros':miembros
        })
        print(f"Proyecto {project_id} actualizado correctamente")
    except Exception as e:
        print(f"Error al actualizar el proyecto: {e}")

def obtener_proyecto_por_id(uid, project_id):
    try:
        proyecto_ref = db.collection('usuario').document(uid).collection('proyectos').document(project_id)
        proyecto = proyecto_ref.get()
        if proyecto.exists:
            return proyecto.to_dict()
        else:
            return None
    except Exception as e:
        print(f"Error al obtener el proyecto: {e}")
        return None

def crear_tarea(uid, project_id, data):
    try:
        # Obtener una referencia al documento donde se guardarán los datos
        proyecto_ref = db.collection('usuario').document(uid).collection('proyectos').document(project_id)
        
        # Crear una subcolección llamada "tareas" dentro del documento del proyecto
        tareas_ref = proyecto_ref.collection('tareas')
        
        # Agregar los datos a un nuevo documento dentro de la subcolección "tareas"
        tarea_ref = tareas_ref.add(data)
        
        # Si llegamos hasta aquí, la tarea se creó correctamente
        return True
    except Exception as e:
        # Si ocurre algún error, imprimirlo y devolver False
        print(f"Error al crear la tarea: {e}")
        return None

def obtener_tareas(uid, project_id):
    try:
        # Obtener una referencia al documento del proyecto
        proyecto_ref = db.collection('usuario').document(uid).collection('proyectos').document(project_id)
        
        # Obtener una referencia a la subcolección "tareas"
        tareas_ref = proyecto_ref.collection('tareas')
        
        # Obtener todos los documentos de la subcolección "tareas"
        tareas_docs = tareas_ref.stream()
        
        # Crear una lista para almacenar las tareas
        tareas = []
        
        # Iterar sobre los documentos y agregar sus datos a la lista
        for doc in tareas_docs:
            tarea = doc.to_dict()
            tarea['id'] = doc.id 
            tarea['estado']=tarea.pop('estado') 
            tarea['titulo']=tarea.pop('titulo') 
            tareas.append(tarea)
        return tareas
    except Exception as e:
        print(f"Error al obtener las tareas: {e}")
        return None

