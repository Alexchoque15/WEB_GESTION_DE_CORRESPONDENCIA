from datetime import datetime

from app import db


class Adjunto(db.Model):

    __tablename__ = 'adjuntos'

    id = db.Column(db.Integer, primary_key=True)

    nombre_original = db.Column(
        db.String(255),
        nullable=False
    )

    nombre_guardado = db.Column(
        db.String(255),
        nullable=False
    )

    ruta = db.Column(
        db.String(500),
        nullable=False
    )

    extension = db.Column(
        db.String(20)
    )

    peso = db.Column(
        db.Integer
    )

    fecha_subida = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    entrada_id = db.Column(
        db.Integer,
        db.ForeignKey('correspondencia_entrada.id')
    )

    salida_id = db.Column(
        db.Integer,
        db.ForeignKey('correspondencia_salida.id')
    )

    def __repr__(self):
        return f'<Adjunto {self.nombre_original}>'