from flask import Blueprint
from flask import request
from flask import redirect
from flask import flash

from app import db

from app.models.correspondencia_entrada import CorrespondenciaEntrada


entrada_bp = Blueprint(
    'entrada_bp',
    __name__
)


@entrada_bp.route(
    '/entrada/guardar',
    methods=['POST']
)
def guardar_entrada():

    nueva = CorrespondenciaEntrada(

        hoja_ruta=request.form.get('hoja_ruta'),
        cite=request.form.get('cite'),
        remitente=request.form.get('remitente'),
        institucion_remitente=request.form.get('institucion_remitente'),
        referencia=request.form.get('referencia'),
        detalle=request.form.get('detalle'),
        prioridad=request.form.get('prioridad'),
        estado=request.form.get('estado'),
        area_destino=request.form.get('area_destino'),
        observaciones=request.form.get('observaciones')

    )

    db.session.add(nueva)

    db.session.commit()

    flash(
        'Correspondencia registrada correctamente',
        'success'
    )

    return redirect('/entrada')