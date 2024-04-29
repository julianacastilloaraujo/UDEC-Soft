class MiembroEquipo:
    def __init__(self,  nombre, cargo, habilidades):
        self.nombre = nombre
        self.cargo = cargo
        self.habilidad = habilidades
        

    def formato_doc(self):
        return {
            'nombre': self.nombre,
            'cargo': self.cargo,
            'habilidades': self.habilidades

        }