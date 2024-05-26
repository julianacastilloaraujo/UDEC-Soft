import firebase_admin
from firebase_admin import credentials, firestore, auth,storage
import requests

# Inicializa Firestore DB
firebase_sdk = credentials.Certificate('src/udecsoft-8be27-firebase-adminsdk-wpz3v-9650bee75f.json')
firebase_admin.initialize_app(firebase_sdk, {
    'storageBucket': 'gs://udecsoft-8be27.appspot.com'
})
db = firestore.client()

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

def obtener_actividades():
    try:
        actividades_ref = db.collection('Actividades')
        actividades = actividades_ref.stream()
        lista_actividades = []
        for actividad in actividades:
            actividad_data = actividad.to_dict()
            actividad_data['id'] = actividad.id 
            actividad_data['descripcion'] = actividad_data.pop('descripcion')  
            actividad_data['imagen_url'] = actividad_data.pop('imagen_url')  
            actividad_data['titulo'] = actividad_data.pop('titulo')  
            lista_actividades.append(actividad_data)
        return lista_actividades
    except Exception as e:
        print(f"Error al obtener las actividades: {e}")
        return None
    
def actualizar_rol_usuario(user_id, nuevo_rol):
    try:
        user_ref = db.collection('usuario').document(user_id)
        user_ref.update({'rol': nuevo_rol})
        return True
    except Exception as e:
        return False
    

def upload_image_to_storage(imagen):
    try:
        # Sube la imagen a Firebase Storage
        blob = storage.bucket().blob(imagen.filename)
        blob.upload_from_file(imagen)
        
        # Establece los permisos de acceso público para el objeto
        blob.make_public()
        
        # Devuelve la URL de descarga de la imagen
        return blob.public_url
    except Exception as e:
        # Maneja cualquier error que pueda ocurrir durante la carga de la imagen
        print(f'Ocurrió un error al cargar la imagen: {str(e)}')
        return None

def agregar_actividad(data):
    doc_ref = db.collection('Actividades').add(data)
    return doc_ref[1].id

def obtener_dato(id):
    doc_ref = db.collection('datos').document(id)
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()
    else:
        return None

def actualizar_actividad(id, data):
    try:
        doc_ref = db.collection('Actividades').document(id)
        doc_ref.update(data)
        return True
    except Exception as e:
        print(f"Error al actualizar la actividad: {e}")
        return False

def eliminar_actividad(actividad_id):
    try:
        print("Eliminando actividad con ID:", actividad_id)
        # Eliminar la actividad de la base de datos
        db.collection('Actividades').document(actividad_id).delete()
        return True
    except Exception as e:
        print(f"Error al eliminar la actividad: {e}")
        return False
