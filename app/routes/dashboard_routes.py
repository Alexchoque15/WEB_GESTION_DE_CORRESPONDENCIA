import pandas as pd
import os

from datetime import datetime
from io import BytesIO
from xhtml2pdf import pisa
from flask import render_template_string

from flask import make_response
from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import flash
from flask import current_app

from werkzeug.utils import secure_filename

from app import db

from app.models.correspondencia_entrada import CorrespondenciaEntrada
from app.models.correspondencia_salida import CorrespondenciaSalida


dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
def home():

    entradas = CorrespondenciaEntrada.query.order_by(
        CorrespondenciaEntrada.id.desc()
    ).limit(5).all()

    salidas = CorrespondenciaSalida.query.order_by(
        CorrespondenciaSalida.id.desc()
    ).limit(5).all()

    return render_template(
        'dashboard/index.html',
        entradas=entradas,
        salidas=salidas
    )


@dashboard_bp.route('/entrada')
def entrada():

    correspondencias = CorrespondenciaEntrada.query.filter_by(
        activo=True
    ).order_by(
        CorrespondenciaEntrada.id.desc()
    ).all()

    return render_template(
        'correspondencia/entrada.html',
        correspondencias=correspondencias
    )

@dashboard_bp.route('/entrada/archivados')
def entrada_archivados():

    correspondencias = CorrespondenciaEntrada.query.filter_by(
        activo=False
    ).order_by(
        CorrespondenciaEntrada.id.desc()
    ).all()

    return render_template(
        'correspondencia/archivados.html',
        correspondencias=correspondencias
    )

@dashboard_bp.route('/entrada/restaurar/<int:id>', methods=['POST'])
def restaurar_entrada(id):

    correspondencia = CorrespondenciaEntrada.query.get_or_404(id)

    try:

        correspondencia.activo = True

        correspondencia.estado = 'RECIBIDO'

        correspondencia.fecha_actualizacion = datetime.now()

        db.session.commit()

        flash(
            'Correspondencia restaurada correctamente',
            'success'
        )

    except Exception as e:

        db.session.rollback()

        flash(
            f'Error al restaurar: {str(e)}',
            'error'
        )

    return redirect(url_for('dashboard.entrada_archivados'))

@dashboard_bp.route('/entrada/eliminar-definitivo/<int:id>', methods=['POST'])
def eliminar_definitivo_entrada(id):

    correspondencia = CorrespondenciaEntrada.query.get_or_404(id)

    try:

        if correspondencia.archivo:

            ruta_archivo = os.path.join(
                current_app.root_path,
                'static',
                'uploads',
                correspondencia.archivo
            )

            if os.path.exists(ruta_archivo):

                os.remove(ruta_archivo)

        db.session.delete(correspondencia)

        db.session.commit()

        flash(
            'Correspondencia eliminada definitivamente',
            'success'
        )

    except Exception as e:

        db.session.rollback()

        flash(
            f'Error al eliminar: {str(e)}',
            'error'
        )

    return redirect(url_for('dashboard.entrada_archivados'))

@dashboard_bp.route('/entrada/guardar', methods=['POST'])
def guardar_entrada():

    try:

        hoja_ruta = request.form.get('hoja_ruta')

        existe = CorrespondenciaEntrada.query.filter_by(
            hoja_ruta=hoja_ruta
        ).first()

        if existe:

            flash('La hoja de ruta ya existe', 'error')

            return redirect(url_for('dashboard.entrada'))

        archivo = request.files.get('archivo_adjunto')

        nombre_archivo = None

        if archivo and archivo.filename != '':

            nombre_archivo = secure_filename(archivo.filename)

            carpeta_upload = os.path.join(
                current_app.root_path,
                'static',
                'uploads'
            )

            os.makedirs(carpeta_upload, exist_ok=True)

            ruta_upload = os.path.join(
                carpeta_upload,
                nombre_archivo
            )

            archivo.save(ruta_upload)

        nueva = CorrespondenciaEntrada(

            hoja_ruta=request.form.get('hoja_ruta'),

            cite=request.form.get('cite'),

            remitente=request.form.get('remitente'),

            institucion_remitente=request.form.get(
                'institucion_remitente'
            ),

            referencia=request.form.get('referencia'),

            detalle=request.form.get('detalle'),

            prioridad=request.form.get('prioridad'),

            estado=request.form.get('estado'),

            area_destino=request.form.get('area_destino'),

            fecha_documento=request.form.get(
                'fecha_documento'
            ) or None,

            fecha_limite=request.form.get(
                'fecha_limite'
            ) or None,

            requiere_respuesta=True if request.form.get(
                'requiere_respuesta'
            ) else False,

            urgente=True if request.form.get(
                'documento_urgente'
            ) else False,

            observaciones=request.form.get('observaciones'),

            archivo=nombre_archivo,

            fecha_registro=datetime.now(),

            usuario_id=1
        )

        db.session.add(nueva)

        db.session.commit()

        flash(
            'Correspondencia registrada correctamente',
            'success'
        )

    except Exception as e:

        db.session.rollback()

        flash(
            f'Error al guardar: {str(e)}',
            'error'
        )

    return redirect(url_for('dashboard.entrada'))


@dashboard_bp.route('/entrada/ver/<int:id>')
def ver_entrada(id):

    entrada = CorrespondenciaEntrada.query.get_or_404(id)

    return render_template(
        'correspondencia/ver_entrada.html',
        entrada=entrada
    )


@dashboard_bp.route('/entrada/editar/<int:id>', methods=['POST'])
def editar_entrada(id):

    correspondencia = CorrespondenciaEntrada.query.get_or_404(id)

    try:

        correspondencia.hoja_ruta = request.form.get('hoja_ruta')
        correspondencia.cite = request.form.get('cite')
        correspondencia.fecha_documento = request.form.get('fecha_documento') or None

        correspondencia.remitente = request.form.get('remitente')

        correspondencia.institucion_remitente = request.form.get('institucion_remitente')

        correspondencia.referencia = request.form.get('referencia')

        correspondencia.detalle = request.form.get('detalle')

        correspondencia.prioridad = request.form.get('prioridad')

        correspondencia.estado = request.form.get('estado')

        correspondencia.area_destino = request.form.get('area_destino')

        correspondencia.fecha_limite = request.form.get('fecha_limite') or None

        correspondencia.urgente = True if request.form.get('urgente') else False

        correspondencia.requiere_respuesta = True if request.form.get('requiere_respuesta') else False

        correspondencia.observaciones = request.form.get('observaciones')

        archivo = request.files.get('archivo')

        if archivo and archivo.filename != '':

            nombre_archivo = archivo.filename

            ruta_upload = os.path.join(
                current_app.root_path,
                'static/uploads',
                nombre_archivo
            )

            archivo.save(ruta_upload)

            correspondencia.archivo = nombre_archivo

        db.session.commit()

        flash('Correspondencia actualizada correctamente', 'success')

    except Exception as e:

        db.session.rollback()

        flash(f'Error al actualizar: {str(e)}', 'error')

    return redirect(url_for('dashboard.entrada'))

@dashboard_bp.route('/entrada/eliminar/<int:id>', methods=['POST'])
def eliminar_entrada(id):

    correspondencia = CorrespondenciaEntrada.query.get_or_404(id)

    try:

        correspondencia.activo = False

        correspondencia.estado = 'ARCHIVADO'

        correspondencia.fecha_actualizacion = datetime.now()

        db.session.commit()

        flash(
            'Correspondencia archivada correctamente',
            'success'
        )

    except Exception as e:

        db.session.rollback()

        flash(
            f'Error al archivar: {str(e)}',
            'error'
        )

    return redirect(url_for('dashboard.entrada'))

@dashboard_bp.route('/salida')
def salida():

    correspondencias = CorrespondenciaSalida.query.order_by(
        CorrespondenciaSalida.id.desc()
    ).all()

    return render_template(
        'correspondencia/salida.html',
        correspondencias=correspondencias
    )


@dashboard_bp.route('/salida/guardar', methods=['POST'])
def guardar_salida():

    try:

        nueva = CorrespondenciaSalida(

            hoja_ruta=request.form.get('hoja_ruta'),

            cite=request.form.get('cite'),

            destinatario=request.form.get('destinatario'),

            institucion_destino=request.form.get(
                'institucion_destino'
            ),

            referencia=request.form.get('referencia'),

            detalle=request.form.get('detalle'),

            prioridad=request.form.get('prioridad'),

            estado=request.form.get('estado'),

            observaciones=request.form.get('observaciones')

        )

        db.session.add(nueva)

        db.session.commit()

        flash(
            'Correspondencia de salida registrada',
            'success'
        )

    except Exception as e:

        db.session.rollback()

        flash(
            f'Error: {str(e)}',
            'error'
        )

    return redirect(url_for('dashboard.salida'))

@dashboard_bp.route('/entrada/exportar/pdf')
def exportar_entrada_pdf():

    correspondencias = CorrespondenciaEntrada.query.order_by(
        CorrespondenciaEntrada.id.desc()
    ).all()

    html = render_template_string("""

    <html>

    <head>

        <style>

            body{
                font-family: Arial;
                font-size: 12px;
            }

            h2{
                text-align:center;
                margin-bottom:20px;
            }

            table{
                width:100%;
                border-collapse: collapse;
            }

            th, td{
                border:1px solid #ccc;
                padding:6px;
            }

            th{
                background:#111827;
                color:white;
            }

        </style>

    </head>

    <body>

        <h2>Reporte Correspondencia Entrada</h2>

        <table>

            <thead>

                <tr>

                    <th>ID</th>
                    <th>Hoja Ruta</th>
                    <th>CITE</th>
                    <th>Remitente</th>
                    <th>Referencia</th>
                    <th>Estado</th>
                    <th>Prioridad</th>

                </tr>

            </thead>

            <tbody>

                {% for c in correspondencias %}

                <tr>

                    <td>{{ c.id }}</td>
                    <td>{{ c.hoja_ruta }}</td>
                    <td>{{ c.cite }}</td>
                    <td>{{ c.remitente }}</td>
                    <td>{{ c.referencia }}</td>
                    <td>{{ c.estado }}</td>
                    <td>{{ c.prioridad }}</td>

                </tr>

                {% endfor %}

            </tbody>

        </table>

    </body>

    </html>

    """, correspondencias=correspondencias)

    pdf = BytesIO()

    pisa.CreatePDF(html, dest=pdf)

    response = make_response(pdf.getvalue())

    response.headers['Content-Type'] = 'application/pdf'

    response.headers['Content-Disposition'] = (
        'attachment; filename=correspondencia_entrada.pdf'
    )

    return response


@dashboard_bp.route('/entrada/exportar/excel')
def exportar_entrada_excel():

    correspondencias = CorrespondenciaEntrada.query.order_by(
        CorrespondenciaEntrada.id.desc()
    ).all()

    datos = []

    for c in correspondencias:

        datos.append({

            'ID': c.id,
            'Hoja Ruta': c.hoja_ruta,
            'CITE': c.cite,
            'Remitente': c.remitente,
            'Institución': c.institucion_remitente,
            'Referencia': c.referencia,
            'Detalle': c.detalle,
            'Prioridad': c.prioridad,
            'Estado': c.estado,
            'Área': c.area_destino,
            'Urgente': 'SI' if c.urgente else 'NO',
            'Respuesta': 'SI' if c.requiere_respuesta else 'NO'

        })

    df = pd.DataFrame(datos)

    output = BytesIO()

    with pd.ExcelWriter(output, engine='openpyxl') as writer:

        df.to_excel(
            writer,
            index=False,
            sheet_name='Correspondencia'
        )

    response = make_response(output.getvalue())

    response.headers[
        'Content-Disposition'
    ] = 'attachment; filename=correspondencia_entrada.xlsx'

    response.headers[
        'Content-type'
    ] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

    return response
