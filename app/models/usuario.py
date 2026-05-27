from datetime import datetime

from flask_login import UserMixin

from app import db


class Usuario(UserMixin, db.Model):

    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)

    nombres = db.Column(
        db.String(150),
        nullable=False
    )

    apellidos = db.Column(
        db.String(150),
        nullable=False
    )

    usuario = db.Column(
        db.String(80),
        unique=True,
        nullable=False
    )

    correo = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )

    telefono = db.Column(db.String(30))

    cargo = db.Column(db.String(120))

    estado = db.Column(
        db.Boolean,
        default=True
    )

    fecha_creacion = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    rol_id = db.Column(
        db.Integer,
        db.ForeignKey('roles.id'),
        nullable=False
    )

    entradas = db.relationship(
        'CorrespondenciaEntrada',
        backref='usuario_registro',
        lazy=True
    )

    salidas = db.relationship(
        'CorrespondenciaSalida',
        backref='usuario_salida',
        lazy=True
    )

    seguimientos = db.relationship(
        'Seguimiento',
        backref='usuario_seguimiento',
        lazy=True
    )

    def __repr__(self):
        return f'<Usuario {self.usuario}>'