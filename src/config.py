from pymongo import MongoClient
import certifi

Mongo = MONGO ='mongodb+srv://juliana:ucundinamarca@cluster0.kd118a2.mongodb.net/'
certifi = certifi.where()

def conexion():
    try:
        client = MongoClient(Mongo,tlsCAfile=certifi)
        db =client["bd_miembroequipo"]
        print('Conexion Exitosa')
    except ConnectionError:
      print('Error de conexion')
    return db

conexion()