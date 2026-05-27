from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import flash

from app import db

from app.models.correspondencia_salida import CorrespondenciaSalida


salida_bp = Blueprint(
    'salida',
    __name__
)


@salida_bp.route('/salida')
def salida():

    correspondencias = CorrespondenciaSalida.query.order_by(
        CorrespondenciaSalida.id.desc()
    ).all()

    return render_template(
        'salida/index.html',
        correspondencias=correspondencias
    )


@salida_bp.route('/salida/guardar', methods=['POST'])
def guardar_salida():

    try:

        nueva = CorrespondenciaSalida(

            hoja_ruta=request.form['hoja_ruta'],

            cite=request.form.get('cite'),

            destinatario=request.form['destinatario'],

            institucion_destino=request.form.get(
                'institucion_destino'
            ),

            referencia=request.form['referencia'],

            detalle=request.form.get('detalle'),

            prioridad=request.form.get('prioridad'),

            estado=request.form.get('estado'),

            area_remitente=request.form.get(
                'area_remitente'
            ),

            observaciones=request.form.get(
                'observaciones'
            ),

            usuario_id=1

        )

        db.session.add(nueva)

        db.session.commit()

        flash(
            'Correspondencia de salida registrada',
            'success'
        )

    except Exception as e:

        db.session.rollback()

        print(e)

        flash(
            f'Error: {str(e)}',
            'danger'
        )

    return redirect(
        url_for('salida.salida')
    )