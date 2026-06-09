from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import flash

from flask_login import login_required
from flask_login import current_user

from werkzeug.security import (
    check_password_hash,
    generate_password_hash
)

from app import db

from app.models.usuario import Usuario
from app.models.rol import Rol
from app.models.correspondencia_entrada import CorrespondenciaEntrada
from app.models.correspondencia_salida import CorrespondenciaSalida

from app.utils.roles import rol_requerido
from app.utils.auditoria import registrar_auditoria

usuario_bp = Blueprint(
    'usuario',
    __name__,
    url_prefix='/usuario'
)

CLAVE_MASTER = "admin123"


# ==========================
# PERFIL
# ==========================

@usuario_bp.route('/perfil')
@login_required
def perfil():

    return render_template(
        'usuario/perfil.html',
        usuario=current_user
    )


# ==========================
# LISTAR USUARIOS
# ==========================

@usuario_bp.route('/listar')
@login_required
@rol_requerido('ADMINISTRADOR')
def listar_usuarios():

    usuarios = Usuario.query.order_by(
        Usuario.id
    ).all()

    return render_template(
        'usuario/listar.html',
        usuarios=usuarios
    )


# ==========================
# GUARDAR USUARIO
# ==========================

@usuario_bp.route(
    '/guardar',
    methods=['POST']
)
@login_required
@rol_requerido('ADMINISTRADOR')
def guardar_usuario():

    rol_nombre = request.form.get(
        'rol'
    )

    rol = Rol.query.filter_by(
        nombre=rol_nombre
    ).first()

    if not rol:

        flash(
            'Rol no encontrado',
            'danger'
        )

        return redirect(
            url_for(
                'usuario.listar_usuarios'
            )
        )

    existe = Usuario.query.filter_by(
        usuario=request.form.get(
            'usuario'
        )
    ).first()

    if existe:

        flash(
            'El usuario ya existe',
            'danger'
        )

        return redirect(
            url_for(
                'usuario.listar_usuarios'
            )
        )

    nuevo = Usuario(

        nombres=request.form.get(
            'nombres'
        ),

        apellidos=request.form.get(
            'apellidos'
        ),

        usuario=request.form.get(
            'usuario'
        ),

        correo=request.form.get(
            'correo'
        ),

        password=generate_password_hash(
            request.form.get(
                'password'
            )
        ),

        rol=rol_nombre,

        rol_id=rol.id,

        estado=True

    )

    db.session.add(
        nuevo
    )

    db.session.commit()

    registrar_auditoria(
        'CREAR',
        'USUARIO'
    )

    flash(
        'Usuario creado correctamente',
        'success'
    )

    return redirect(
        url_for(
            'usuario.listar_usuarios'
        )
    )


# ==========================
# RESETEAR BASE DE DATOS
# ==========================

@usuario_bp.route(
    '/resetear-bd',
    methods=['POST']
)
@login_required
@rol_requerido(
    'ADMINISTRADOR'
)
def resetear_bd():

    password = request.form.get(
        'password'
    )

    admin = Usuario.query.filter_by(
        id=current_user.id
    ).first()

    if not check_password_hash(
        admin.password,
        password
    ):

        flash(
            'Contraseña incorrecta',
            'danger'
        )

        return redirect(
            url_for(
                'usuario.perfil'
            )
        )

    CorrespondenciaEntrada.query.delete()

    CorrespondenciaSalida.query.delete()

    db.session.commit()

    registrar_auditoria(
        'RESETEAR',
        'BASE_DATOS'
    )

    flash(
        'Base de datos reiniciada correctamente',
        'success'
    )

    return redirect(
        url_for(
            'usuario.perfil'
        )
    )


# ==========================
# VER USUARIO
# ==========================

@usuario_bp.route('/ver/<int:id>')
@login_required
@rol_requerido('ADMINISTRADOR')
def ver_usuario(id):

    usuario = Usuario.query.get_or_404(
        id
    )

    return render_template(
        'usuario/ver.html',
        usuario=usuario
    )


# ==========================
# ELIMINAR USUARIO
# ==========================

@usuario_bp.route(
    '/eliminar/<int:id>',
    methods=['POST']
)
@login_required
@rol_requerido('ADMINISTRADOR')
def eliminar_usuario(id):

    usuario = Usuario.query.get_or_404(
        id
    )

    if usuario.id == current_user.id:

        flash(
            'No puede eliminar su propia cuenta',
            'danger'
        )

        return redirect(
            url_for(
                'usuario.listar_usuarios'
            )
        )

    db.session.delete(
        usuario
    )

    db.session.commit()

    registrar_auditoria(
        'ELIMINAR',
        'USUARIO'
    )

    flash(
        'Usuario eliminado correctamente',
        'success'
    )

    return redirect(
        url_for(
            'usuario.listar_usuarios'
        )
    )


# ==========================
# BLOQUEAR USUARIO
# ==========================

@usuario_bp.route(
    '/bloquear/<int:id>',
    methods=['POST']
)
@login_required
@rol_requerido('ADMINISTRADOR')
def bloquear_usuario(id):

    usuario = Usuario.query.get_or_404(
        id
    )

    usuario.estado = False

    db.session.commit()

    registrar_auditoria(
        'BLOQUEAR',
        'USUARIO'
    )

    flash(
        'Usuario bloqueado',
        'warning'
    )

    return redirect(
        url_for(
            'usuario.listar_usuarios'
        )
    )


# ==========================
# ACTIVAR USUARIO
# ==========================

@usuario_bp.route(
    '/activar/<int:id>',
    methods=['POST']
)
@login_required
@rol_requerido('ADMINISTRADOR')
def activar_usuario(id):

    usuario = Usuario.query.get_or_404(
        id
    )

    usuario.estado = True

    db.session.commit()

    registrar_auditoria(
        'ACTIVAR',
        'USUARIO'
    )

    flash(
        'Usuario activado correctamente',
        'success'
    )

    return redirect(
        url_for(
            'usuario.listar_usuarios'
        )
    )