from datetime import datetime

from app import db


class Seguimiento(db.Model):

    __tablename__ = 'seguimientos'

    id = db.Column(db.Integer, primary_key=True)

    accion = db.Column(
        db.String(255),
        nullable=False
    )

    observacion = db.Column(db.Text)

    estado = db.Column(
        db.String(50)
    )

    fecha = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    entrada_id = db.Column(
        db.Integer,
        db.ForeignKey('correspondencia_entrada.id')
    )

    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey('usuarios.id'),
        nullable=False
    )

    def __repr__(self):
        return f'<Seguimiento {self.id}>'