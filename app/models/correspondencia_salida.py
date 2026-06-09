from datetime import datetime

from app import db

class CorrespondenciaSalida(db.Model):

    __tablename__ = 'correspondencia_salida'

    id = db.Column(db.Integer, primary_key=True)

    hoja_ruta = db.Column(db.String(50), unique=True, nullable=False)

    cite = db.Column(db.String(100))

    destinatario = db.Column(db.String(255), nullable=False)

    institucion_destino = db.Column(db.String(255))

    referencia = db.Column(db.String(500), nullable=False)

    detalle = db.Column(db.Text)

    prioridad = db.Column(db.String(30), default='MEDIA')

    estado = db.Column(db.String(50), default='ENVIADO')

    fecha_envio = db.Column(db.Date)

    medio_envio = db.Column(db.String(100))

    numero_guia = db.Column(db.String(100))

    archivo = db.Column(db.String(255))

    fecha_entrega = db.Column(db.Date)

    recibido_por = db.Column(db.String(255))

    confirmado = db.Column(
        db.Boolean,
        default=False
    )

    observaciones = db.Column(db.Text)

    fecha_registro = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey('usuarios.id')
    )

    entrada_id = db.Column(
        db.Integer,
        db.ForeignKey('correspondencia_entrada.id')
    )

    activo = db.Column(
        db.Boolean,
        default=True
    )

    def __repr__(self):
        return f'<Salida {self.hoja_ruta}>'