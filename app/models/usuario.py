from datetime import datetime
from flask_login import UserMixin
from app import db

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

class Usuario(UserMixin, db.Model):

    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)

    intentos_fallidos = db.Column(
        db.Integer,
        default=0
    )

    bloqueado_hasta = db.Column(
        db.DateTime,
        nullable=True
    )

    ultimo_login = db.Column(
        db.DateTime,
        nullable=True
    )

    ultima_ip = db.Column(
        db.String(50),
        nullable=True
    )

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

    rol = db.Column(
        db.String(30),
        nullable=False,
        default='PERSONAL'
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

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(
            self.password,
            password
        )

    def __repr__(self):
        return f'<Usuario {self.usuario}>'