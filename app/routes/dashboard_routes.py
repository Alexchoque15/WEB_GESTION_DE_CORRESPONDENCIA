import pandas as pd
import os
import tempfile
import uuid

ALLOWED_EXTENSIONS = {
    'pdf',
    'doc',
    'docx',
    'xls',
    'xlsx',
    'jpg',
    'jpeg',
    'png'
}

def allowed_file(filename):

    return (
        '.' in filename
        and filename.rsplit(
            '.',
            1
        )[1].lower() in ALLOWED_EXTENSIONS
    )

from datetime import datetime
from io import BytesIO
from xhtml2pdf import pisa
from flask import send_file
from flask import render_template_string
from flask import make_response
from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import flash
from flask import current_app
from flask_login import login_required
from werkzeug.utils import secure_filename
from app import db
from app.models.correspondencia_entrada import CorrespondenciaEntrada
from app.models.correspondencia_salida import CorrespondenciaSalida
from app.utils.auditoria import registrar_auditoria
from app.utils.roles import rol_requerido
from flask import render_template
from sqlalchemy import extract,func
from datetime import date, datetime
dashboard_bp = Blueprint(
    'dashboard',
    __name__
)

@dashboard_bp.route('/')
@login_required
def home():

    tipo = request.args.get('tipo')
    prioridad = request.args.get('prioridad')

    mes_actual = datetime.now().month
    anio_actual = datetime.now().year

    mes_anterior = 12 if mes_actual == 1 else mes_actual - 1
    anio_anterior = anio_actual - 1 if mes_actual == 1 else anio_actual

    entradas = CorrespondenciaEntrada.query.order_by(
        CorrespondenciaEntrada.id.desc()
    ).limit(5).all()

    salidas = CorrespondenciaSalida.query.order_by(
        CorrespondenciaSalida.id.desc()
    ).limit(5).all()

    entradas_hoy = CorrespondenciaEntrada.query.filter(
        func.date(CorrespondenciaEntrada.fecha_registro) == date.today()
    ).count()

    salidas_hoy = CorrespondenciaSalida.query.filter(
        func.date(CorrespondenciaSalida.fecha_registro) == date.today()
    ).count()

    entradas_actual = CorrespondenciaEntrada.query.filter(
        extract('month', CorrespondenciaEntrada.fecha_registro) == mes_actual,
        extract('year', CorrespondenciaEntrada.fecha_registro) == anio_actual
    ).count()

    entradas_anterior = CorrespondenciaEntrada.query.filter(
        extract('month', CorrespondenciaEntrada.fecha_registro) == mes_anterior,
        extract('year', CorrespondenciaEntrada.fecha_registro) == anio_anterior
    ).count()

    if entradas_anterior:
        porcentaje_entrada = round(
            ((entradas_actual - entradas_anterior) / entradas_anterior) * 100
        )
    else:
        porcentaje_entrada = 100

    salidas_actual = CorrespondenciaSalida.query.filter(
        extract('month', CorrespondenciaSalida.fecha_registro) == mes_actual,
        extract('year', CorrespondenciaSalida.fecha_registro) == anio_actual
    ).count()

    salidas_anterior = CorrespondenciaSalida.query.filter(
        extract('month', CorrespondenciaSalida.fecha_registro) == mes_anterior,
        extract('year', CorrespondenciaSalida.fecha_registro) == anio_anterior
    ).count()

    if salidas_anterior:
        porcentaje_salida = round(
            ((salidas_actual - salidas_anterior) / salidas_anterior) * 100
        )
    else:
        porcentaje_salida = 100

    procesados_actual = CorrespondenciaSalida.query.filter(
        CorrespondenciaSalida.estado == 'ENTREGADO',
        extract('month', CorrespondenciaSalida.fecha_registro) == mes_actual
    ).count()

    procesados_anterior = CorrespondenciaSalida.query.filter(
        CorrespondenciaSalida.estado == 'ENTREGADO',
        extract('month', CorrespondenciaSalida.fecha_registro) == mes_anterior
    ).count()

    if procesados_anterior:
        porcentaje_procesado = round(
            ((procesados_actual - procesados_anterior) /
            procesados_anterior) * 100
        )
    else:
        porcentaje_procesado = 100

    urgentes_actual = (
        CorrespondenciaEntrada.query.filter_by(
            prioridad='URGENTE',
            activo=True
        ).count()
        +
        CorrespondenciaSalida.query.filter_by(
            prioridad='URGENTE',
            activo=True
        ).count()
    )

    urgentes_anterior = CorrespondenciaEntrada.query.filter(
        CorrespondenciaEntrada.prioridad == 'URGENTE',
        extract('month',
                CorrespondenciaEntrada.fecha_registro) == mes_anterior,
        extract('year',
                CorrespondenciaEntrada.fecha_registro) == anio_anterior
    ).count()

    urgentes_anterior += CorrespondenciaSalida.query.filter(
        CorrespondenciaSalida.prioridad == 'URGENTE',
        extract('month',
                CorrespondenciaSalida.fecha_registro) == mes_anterior,
        extract('year',
                CorrespondenciaSalida.fecha_registro) == anio_anterior
    ).count()

    if urgentes_anterior:
        porcentaje_urgente = round(
            ((urgentes_actual - urgentes_anterior) /
            urgentes_anterior) * 100
        )
    else:
        porcentaje_urgente = 0

    procesados_hoy = (
        CorrespondenciaEntrada.query.filter_by(
            estado='RESPONDIDO'
        ).count()
        +
        CorrespondenciaSalida.query.filter_by(
            estado='ENTREGADO'
        ).count()
    )

    urgentes_pendientes = (
        CorrespondenciaEntrada.query.filter_by(
            prioridad='URGENTE',
            activo=True
        ).count()
        +
        CorrespondenciaSalida.query.filter_by(
            prioridad='URGENTE',
            activo=True
        ).count()
    )

    movimientos = []

    for e in entradas:
        movimientos.append({
            'tipo': 'ENTRADA',
            'referencia': e.referencia,
            'fecha_registro': e.fecha_registro
        })

    for s in salidas:
        movimientos.append({
            'tipo': 'SALIDA',
            'referencia': s.referencia,
            'fecha_registro': s.fecha_registro
        })

    movimientos.sort(
        key=lambda x: x['fecha_registro'],
        reverse=True
    )

    ultimos = []

    for e in entradas:
        ultimos.append({
            'tipo': 'ENTRADA',
            'hoja_ruta': e.hoja_ruta,
            'referencia': e.referencia,
            'area': e.area_destino,
            'prioridad': e.prioridad,
            'estado': e.estado,
            'fecha': e.fecha_registro
        })

    for s in salidas:
        ultimos.append({
            'tipo': 'SALIDA',
            'hoja_ruta': s.hoja_ruta,
            'referencia': s.referencia,
            'area': s.institucion_destino,
            'prioridad': s.prioridad,
            'estado': s.estado,
            'fecha': s.fecha_registro
        })

    ultimos = sorted(
        ultimos,
        key=lambda x: x['fecha'],
        reverse=True
    )

    if tipo:
        ultimos = [
            x for x in ultimos
            if x['tipo'] == tipo
        ]

    if prioridad:
        ultimos = [
            x for x in ultimos
            if x['prioridad'] == prioridad
        ]

    total_entradas = CorrespondenciaEntrada.query.filter_by(
        activo=True
    ).count()

    total_salidas = CorrespondenciaSalida.query.filter_by(
        activo=True
    ).count()

    total_procesados = (
        CorrespondenciaEntrada.query.filter_by(
            estado='RESPONDIDO'
        ).count()
        +
        CorrespondenciaSalida.query.filter_by(
            estado='ENTREGADO'
        ).count()
    )

    total_urgentes = (
        CorrespondenciaEntrada.query.filter_by(
            prioridad='URGENTE',
            activo=True
        ).count()
        +
        CorrespondenciaSalida.query.filter_by(
            prioridad='URGENTE',
            activo=True
        ).count()
    )

    entradas_mes = [0] * 12
    salidas_mes = [0] * 12

    for e in CorrespondenciaEntrada.query.all():
        if e.fecha_registro:
            entradas_mes[e.fecha_registro.month - 1] += 1

    for s in CorrespondenciaSalida.query.all():
        if s.fecha_registro:
            salidas_mes[s.fecha_registro.month - 1] += 1

    movimientos = []

    for e in CorrespondenciaEntrada.query.order_by(
        CorrespondenciaEntrada.fecha_registro.desc()
    ).limit(10):

        movimientos.append({
            'tipo': 'ENTRADA',
            'referencia': e.referencia,
            'fecha_registro': e.fecha_registro
        })

    for s in CorrespondenciaSalida.query.order_by(
        CorrespondenciaSalida.fecha_registro.desc()
    ).limit(10):

        movimientos.append({
            'tipo': 'SALIDA',
            'referencia': s.referencia,
            'fecha_registro': s.fecha_registro
        })

    movimientos = sorted(
        movimientos,
        key=lambda x: x['fecha_registro'],
        reverse=True
    )

    return render_template(
        'dashboard/index.html',
        entradas=entradas,
        salidas=salidas,
        movimientos=movimientos[:10],
        total_entradas=total_entradas,
        total_salidas=total_salidas,
        total_procesados=total_procesados,
        total_urgentes=total_urgentes,
        entradas_mes=entradas_mes,
        salidas_mes=salidas_mes,
        entradas_hoy=entradas_hoy,
        salidas_hoy=salidas_hoy,
        procesados_hoy=procesados_hoy,
        urgentes_pendientes=urgentes_pendientes,
        porcentaje_entrada=porcentaje_entrada,
        porcentaje_salida=porcentaje_salida,
        porcentaje_procesado=porcentaje_procesado,
        porcentaje_urgente=porcentaje_urgente,
        ultimos=ultimos
    )


@dashboard_bp.route('/entrada')
@login_required
def entrada():
    correspondencias = CorrespondenciaEntrada.query.filter_by(
        activo=True
    ).order_by(
        CorrespondenciaEntrada.id.desc()
    ).all()
    return render_template(
        'correspondencia/entrada.html',
        correspondencias=correspondencias)

@dashboard_bp.route('/archivados')
@login_required
@rol_requerido(
    'ADMINISTRADOR',
    'ARCHIVO'
)
def archivados():

    entradas = CorrespondenciaEntrada.query.filter_by(
        activo=False
    ).order_by(
        CorrespondenciaEntrada.fecha_registro.desc()
    ).all()

    salidas = CorrespondenciaSalida.query.filter_by(
        activo=False
    ).order_by(
        CorrespondenciaSalida.fecha_registro.desc()
    ).all()

    return render_template(
        'correspondencia/archivados.html',
        entradas=entradas,
        salidas=salidas
    )

@dashboard_bp.route('/entrada/archivados')
def entrada_archivados():

    entradas = CorrespondenciaEntrada.query.filter_by(
        activo=False
    ).all()

    return render_template(
        'correspondencia/archivados.html',
        entradas=entradas
    )

@dashboard_bp.route(
    '/entrada/restaurar/<int:id>',
    methods=['POST']
)
def restaurar_entrada(id):

    entrada = CorrespondenciaEntrada.query.get_or_404(id)

    entrada.activo = True

    db.session.commit()

    registrar_auditoria(
        'RESTAURAR',
        'CORRESPONDENCIA_ENTRADA'
    )

    flash(
        'Documento restaurado',
        'success'
    )

    return redirect(
        url_for('dashboard.archivados')
    )

@dashboard_bp.route(
    '/entrada/eliminar-definitivo/<int:id>',
    methods=['POST']
)
def eliminar_definitivo_entrada(id):

    entrada = CorrespondenciaEntrada.query.get_or_404(id)

    db.session.delete(entrada)

    db.session.commit()

    registrar_auditoria(
        'ELIMINAR',
        'CORRESPONDENCIA_ENTRADA'
    )

    flash(
        'Correspondencia eliminada definitivamente',
        'success'
    )

    return redirect(
        url_for('dashboard.archivados')
    )

@dashboard_bp.route(
    '/salida/eliminar-definitivo/<int:id>',
    methods=['POST']
)
def eliminar_definitivo_salida(id):

    salida = CorrespondenciaSalida.query.get_or_404(id)

    db.session.delete(salida)

    db.session.commit()

    registrar_auditoria(
        'ELIMINAR',
        'CORRESPONDENCIA_SALIDA'
    )

    flash(
        'Correspondencia eliminada definitivamente',
        'success'
    )

    return redirect(
        url_for('dashboard.archivados')
    )

@dashboard_bp.route('/entrada/eliminar/<int:id>', methods=['POST'])
def eliminar_entrada(id):

    entrada = CorrespondenciaEntrada.query.get_or_404(id)

    entrada.activo = False

    db.session.commit()

    registrar_auditoria(
        'ARCHIVAR',
        'CORRESPONDENCIA_ENTRADA'
    )

    flash(
        'Documento archivado correctamente',
        'success'
    )

    return redirect(
        url_for('dashboard.entrada')
    )

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

            if not allowed_file(
                archivo.filename
            ):

                flash(
                    'Archivo no permitido',
                    'danger'
                )

                return redirect(
                    url_for(
                        'dashboard.entrada'
                    )
                )

            extension = archivo.filename.rsplit(
                '.',
                1
            )[1].lower()

            nombre_archivo = (
                str(uuid.uuid4())
                + '.'
                + extension
            )

            carpeta_upload = os.path.join(
                current_app.root_path,
                'uploads'
            )

            os.makedirs(
                carpeta_upload,
                exist_ok=True
            )

            ruta_upload = os.path.join(
                carpeta_upload,
                nombre_archivo
            )

            archivo.save(
                ruta_upload
            )
            nombre_archivo = secure_filename(archivo.filename)
            carpeta_upload = os.path.join(
                current_app.root_path,
                'uploads'
            )
            os.makedirs(carpeta_upload, exist_ok=True)
            ruta_upload = os.path.join(
                carpeta_upload,
                nombre_archivo)
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
        registrar_auditoria(
            'CREAR',
            'CORRESPONDENCIA_ENTRADA'
        )
        flash(
            'Correspondencia registrada correctamente',
            'success')
    except Exception as e:
        db.session.rollback()
        flash(
            f'Error al guardar: {str(e)}',
            'error')
    return redirect(url_for('dashboard.entrada'))

@dashboard_bp.route('/entrada/ver/<int:id>')
def ver_entrada(id):
    entrada = CorrespondenciaEntrada.query.get_or_404(id)
    return render_template(
        'correspondencia/ver_entrada.html',
        entrada=entrada)

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
        archivo = request.files.get(
            'archivo'
        )

        if archivo and archivo.filename != '':

            if not allowed_file(
                archivo.filename
            ):

                flash(
                    'Archivo no permitido',
                    'danger'
                )

                return redirect(
                    url_for(
                        'dashboard.entrada'
                    )
                )

            extension = archivo.filename.rsplit(
                '.',
                1
            )[1].lower()

            nombre_archivo = (
                str(uuid.uuid4())
                + '.'
                + extension
            )

            carpeta_upload = os.path.join(
                current_app.root_path,
                'uploads'
            )

            os.makedirs(
                carpeta_upload,
                exist_ok=True
            )

            ruta_upload = os.path.join(
                carpeta_upload,
                nombre_archivo
            )

            archivo.save(
                ruta_upload
            )

            correspondencia.archivo = (
                nombre_archivo
            )
        if archivo and archivo.filename != '':
            nombre_archivo = archivo.filename
            ruta_upload = os.path.join(
                current_app.root_path,
                'static/uploads',
                nombre_archivo)
            archivo.save(ruta_upload)
            correspondencia.archivo = nombre_archivo
        db.session.commit()
        registrar_auditoria(
            'EDITAR',
            'CORRESPONDENCIA_ENTRADA'
        )
        flash('Correspondencia actualizada correctamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar: {str(e)}', 'error')
    return redirect(url_for('dashboard.entrada'))

@dashboard_bp.route('/salida/eliminar/<int:id>', methods=['POST'])
def eliminar_salida(id):

    salida = CorrespondenciaSalida.query.get_or_404(id)

    salida.activo = False

    db.session.commit()
    registrar_auditoria(
        'ARCHIVAR',
        'CORRESPONDENCIA_SALIDA'
    )

    flash(
        'Documento archivado correctamente',
        'success'
    )

    return redirect(
        url_for('dashboard.salida')
    )

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
                font-size: 12px;}
            h2{
                text-align:center;
                margin-bottom:20px;}
            table{
                width:100%;
                border-collapse: collapse;}
            th, td{
                border:1px solid #ccc;
                padding:6px;}
            th{
                background:#111827;
                color:white;}
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
        'attachment; filename=correspondencia_entrada.pdf')
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
            sheet_name='Correspondencia')
    response = make_response(output.getvalue())
    response.headers[
        'Content-Disposition'
    ] = 'attachment; filename=correspondencia_entrada.xlsx'
    response.headers[
        'Content-type'
    ] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    return response

@dashboard_bp.route('/salida')
@login_required
def salida():

    correspondencias = CorrespondenciaSalida.query.filter_by(
        activo=True
    ).order_by(
        CorrespondenciaSalida.id.desc()
    ).all()

    entradas = CorrespondenciaEntrada.query.filter_by(
        activo=True
    ).all()

    total_enviados = CorrespondenciaSalida.query.count()

    total_entregados = CorrespondenciaSalida.query.filter_by(
        estado='ENTREGADO'
    ).count()

    total_pendientes = CorrespondenciaSalida.query.filter_by(
        estado='PENDIENTE'
    ).count()

    total_urgentes = CorrespondenciaSalida.query.filter_by(
        prioridad='URGENTE'
    ).count()

    return render_template(
        'correspondencia/salida.html',
        correspondencias=correspondencias,
        entradas=entradas,
        total_enviados=total_enviados,
        total_entregados=total_entregados,
        total_pendientes=total_pendientes,
        total_urgentes=total_urgentes
    )


@dashboard_bp.route('/salida/guardar', methods=['POST'])
def guardar_salida():

    nueva = CorrespondenciaSalida(

        entrada_id=request.form.get('entrada_id'),

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

        fecha_envio=request.form.get(
            'fecha_envio'
        ) or None,

        medio_envio=request.form.get(
            'medio_envio'
        ),

        numero_guia=request.form.get(
            'numero_guia'
        ),

        fecha_entrega=request.form.get(
            'fecha_entrega'
        ) or None,

        recibido_por=request.form.get(
            'recibido_por'
        ),

        confirmado=True
        if request.form.get(
            'entrega_confirmada'
        )
        else False,

        observaciones=request.form.get(
            'observaciones'
        )
    )

    db.session.add(nueva)

    entrada = CorrespondenciaEntrada.query.get(
        request.form.get('entrada_id')
    )

    if entrada:

        entrada.estado = 'RESPONDIDO'

    db.session.commit()

    registrar_auditoria(
        'CREAR',
        'CORRESPONDENCIA_SALIDA'
    )

    flash(
        'Correspondencia de salida registrada',
        'success'
    )

    return redirect(
        url_for('dashboard.salida')
    )

@dashboard_bp.route('/salida/ver/<int:id>')
def ver_salida(id):

    salida = CorrespondenciaSalida.query.get_or_404(id)

    return render_template(
        'correspondencia/ver_salida.html',
        salida=salida
    )

@dashboard_bp.route(
    '/salida/editar/<int:id>',
    methods=['POST']
)
def editar_salida(id):

    salida = CorrespondenciaSalida.query.get_or_404(id)

    salida.hoja_ruta = request.form['hoja_ruta']
    salida.cite = request.form['cite']
    salida.destinatario = request.form['destinatario']
    salida.institucion_destino = request.form['institucion_destino']
    salida.referencia = request.form['referencia']
    salida.detalle = request.form['detalle']
    salida.prioridad = request.form['prioridad']
    salida.estado = request.form['estado']
    salida.medio_envio = request.form['medio_envio']

    salida.numero_guia = request.form.get(
        'numero_guia'
    )

    salida.recibido_por = request.form[
        'recibido_por'
    ]

    salida.observaciones = request.form[
        'observaciones'
    ]

    # Confirmación de entrega
    salida.confirmado = (
        'confirmado' in request.form
    )

    # Fecha de entrega
    fecha_entrega = request.form.get(
        'fecha_entrega'
    )

    if fecha_entrega:
        salida.fecha_entrega = datetime.strptime(
            fecha_entrega,
            '%Y-%m-%d'
        ).date()

    # Reemplazar archivo si se seleccionó uno nuevo
    archivo = request.files.get(
        'archivo_adjunto'
    )

    if archivo and archivo.filename:

        nombre_archivo = secure_filename(
            archivo.filename
        )

        carpeta_uploads = os.path.join(
            current_app.root_path,
            'static',
            'uploads'
        )

        os.makedirs(
            carpeta_uploads,
            exist_ok=True
        )

        ruta_archivo = os.path.join(
            carpeta_uploads,
            nombre_archivo
        )

        archivo.save(ruta_archivo)

        salida.archivo = nombre_archivo

    db.session.commit()

    registrar_auditoria(
        'EDITAR',
        'CORRESPONDENCIA_SALIDA'
    )

    flash(
        'Correspondencia actualizada correctamente',
        'success'
    )

    return redirect(
        url_for('dashboard.salida')
    )


@dashboard_bp.route('/reporte/salida/pdf')
def reporte_salida_pdf():
    correspondencias = CorrespondenciaSalida.query.all()
    html = render_template(
        'reportes/reporte_salida_pdf.html',
        correspondencias=correspondencias)
    pdf = BytesIO()
    pisa.CreatePDF(
        html,
        dest=pdf)
    response = make_response(
        pdf.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = (
        'attachment; filename=correspondencia_salida.pdf')
    return response

@dashboard_bp.route('/reporte/salida/excel')
def reporte_salida_excel():

    correspondencias = CorrespondenciaSalida.query.all()

    datos = []

    for c in correspondencias:

        datos.append({
            'HR Entrada':
                c.entrada.hoja_ruta if c.entrada else '',
            'CITE Entrada':
                c.entrada.cite if c.entrada else '',
            'HR Salida':
                c.hoja_ruta,
            'CITE Respuesta':
                c.cite,
            'Destinatario':
                c.destinatario,
            'Institución':
                c.institucion_destino,
            'Referencia':
                c.referencia,
            'Estado':
                c.estado
        })

    df = pd.DataFrame(datos)

    archivo = tempfile.NamedTemporaryFile(
        delete=False,
        suffix='.xlsx'
    )

    df.to_excel(
        archivo.name,
        index=False
    )

    return send_file(
        archivo.name,
        as_attachment=True,
        download_name='correspondencia_salida.xlsx'
    )

@dashboard_bp.route(
    '/salida/restaurar/<int:id>',
    methods=['POST']
)
def restaurar_salida(id):

    salida = CorrespondenciaSalida.query.get_or_404(id)

    salida.activo = True

    db.session.commit()

    registrar_auditoria(
        'RESTAURAR',
        'CORRESPONDENCIA_SALIDA'
    )

    flash(
        'Correspondencia restaurada correctamente',
        'success'
    )

    return redirect(
        url_for('dashboard.archivados')
    )