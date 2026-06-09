from flask import Blueprint
from flask import request
from flask import redirect
from flask import flash

from app import db

from app.models.correspondencia_entrada import CorrespondenciaEntrada
from app.utils.roles import rol_requerido
from app.utils.file_security import allowed_file

from flask import render_template

from flask_login import login_required

entrada_bp = Blueprint(
    'entrada_bp',
    __name__
)

@entrada_bp.route('/entrada')
@login_required
@rol_requerido(
    'ADMIN',
    'RECEPCION'
)
def entrada():

    correspondencias = CorrespondenciaEntrada.query.order_by(
        CorrespondenciaEntrada.id.desc()
    ).all()

    return render_template(
        'entrada/index.html',
        correspondencias=correspondencias
    )

@entrada_bp.route(
    '/entrada/guardar',
    methods=['POST']
)
@login_required
@rol_requerido(
    'ADMINISTRADOR',
    'RECEPCION'
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

    archivo = request.files.get(
        'documento'
    )

    if archivo:

        if not allowed_file(
            archivo.filename
        ):

            flash(
                'Tipo de archivo no permitido',
                'danger'
            )

            return redirect(
                request.url
            )

    db.session.add(nueva)

    db.session.commit()

    flash(
        'Correspondencia registrada correctamente',
        'success'
    )

    return redirect('/entrada')