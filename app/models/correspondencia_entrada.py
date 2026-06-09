from datetime import datetime
from app import db
class CorrespondenciaEntrada(db.Model):
    __tablename__ = 'correspondencia_entrada'
    id = db.Column(db.Integer, primary_key=True)
    hoja_ruta = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )
    cite = db.Column(db.String(100))
    remitente = db.Column(
        db.String(255),
        nullable=False
    )
    institucion_remitente = db.Column(
        db.String(255)
    )
    referencia = db.Column(
        db.String(500),
        nullable=False
    )
    detalle = db.Column(db.Text)
    prioridad = db.Column(
        db.String(30),
        default='MEDIA'
    )
    estado = db.Column(
        db.String(50),
        default='RECIBIDO'
    )
    area_destino = db.Column(
        db.String(150)
    )
    fecha_documento = db.Column(db.Date)
    fecha_limite = db.Column(db.Date)
    requiere_respuesta = db.Column(
        db.Boolean,
        default=False
    )
    urgente = db.Column(
        db.Boolean,
        default=False
    )
    observaciones = db.Column(db.Text)
    archivo = db.Column(db.String(255))
    fecha_registro = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )
    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey('usuarios.id'),
    )
    seguimientos = db.relationship(
        'Seguimiento',
        backref='entrada',
        lazy=True
    )
    adjuntos = db.relationship(
        'Adjunto',
        backref='entrada_adjunto',
        lazy=True
    )
    activo = db.Column(db.Boolean, default=True)
    fecha_actualizacion = db.Column(db.DateTime)
    salidas = db.relationship(
        'CorrespondenciaSalida',
        backref='entrada',
        lazy=True
    )
    def __repr__(self):
        return f'<Entrada {self.hoja_ruta}>'