from datetime import datetime

from app import db


class AuditoriaLogin(db.Model):

    __tablename__ = 'auditoria_login'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    usuario = db.Column(
        db.String(80)
    )

    ip = db.Column(
        db.String(100)
    )

    exito = db.Column(
        db.Boolean,
        default=False
    )

    fecha = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )