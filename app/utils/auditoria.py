from flask_login import current_user
from flask import request

from app import db
from app.models.auditoria_sistema import AuditoriaSistema


def registrar_auditoria(
    accion,
    modulo
):

    auditoria = AuditoriaSistema(

        usuario=current_user.usuario,

        accion=accion,

        modulo=modulo,

        ip=request.remote_addr

    )

    db.session.add(
        auditoria
    )

    db.session.commit()