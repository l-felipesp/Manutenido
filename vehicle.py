class Vehicle:
    def __init__(self, id=None, user_id=None, modelo="", placa="", tipo="Carro", oficinas_autorizadas=None):
        self.id = id
        self.user_id = user_id
        self.modelo = modelo
        self.placa = placa
        self.tipo = tipo # Carro, Moto, Caminhão, Bike
        self.oficinas_autorizadas = oficinas_autorizadas if oficinas_autorizadas else []

    def to_dict(self):
        """Converte o objeto para dicionário (formato que o Firebase aceita)"""
        return {
            "user_id": self.user_id,
            "modelo": self.modelo,
            "placa": self.placa,
            "tipo": self.tipo,
            "oficinas_autorizadas": self.oficinas_autorizadas
        }