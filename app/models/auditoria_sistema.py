from datetime import datetime

from app import db


class AuditoriaSistema(db.Model):

    __tablename__ = 'auditoria_sistema'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    usuario = db.Column(
        db.String(100)
    )

    accion = db.Column(
        db.String(100)
    )

    modulo = db.Column(
        db.String(100)
    )

    ip = db.Column(
        db.String(50)
    )

    fecha = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )