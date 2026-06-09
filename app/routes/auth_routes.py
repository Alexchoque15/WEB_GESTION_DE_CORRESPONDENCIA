from app import db
from app import limiter
from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import flash

from flask_login import login_user
from flask_login import logout_user
from flask_login import login_required
from datetime import datetime, timedelta

from app.models.usuario import Usuario
from app.models.auditoria_login import AuditoriaLogin

auth_bp = Blueprint(
    'auth',
    __name__,
    url_prefix='/auth'
)

@auth_bp.route(
    '/login',
    methods=['GET', 'POST']
)
@limiter.limit("5 per minute")
def login():

    if request.method == 'POST':

        username = request.form.get(
            'usuario'
        )

        password = request.form.get(
            'password'
        )

        user = Usuario.query.filter_by(
            usuario=username
        ).first()
        

        if user:

            if user.bloqueado_hasta:

                if user.bloqueado_hasta > datetime.utcnow():

                    flash(
                        'Usuario bloqueado temporalmente. Intente más tarde.',
                        'danger'
                    )

                    return redirect(
                        url_for('auth.login')
                    )

            if user.check_password(password):

                user.intentos_fallidos = 0

                user.bloqueado_hasta = None

                user.ultimo_login = datetime.utcnow()

                user.ultima_ip = request.remote_addr

                db.session.commit()

                registro = AuditoriaLogin(
                    usuario=user.usuario,
                    ip=request.remote_addr,
                    exito=True
                )

                db.session.add(registro)

                db.session.commit()

                login_user(user)

                from flask import session

                session.permanent = True

                return redirect(
                    url_for('dashboard.home')
                )

            else:
                if user.intentos_fallidos is None:
                    user.intentos_fallidos = 0

                user.intentos_fallidos += 1

                if user.intentos_fallidos == 5:

                    bloqueo = 15

                elif user.intentos_fallidos == 10:

                    bloqueo = 60

                elif user.intentos_fallidos >= 15:

                    bloqueo = 1440

                else:

                    bloqueo = None

                if bloqueo:

                    user.bloqueado_hasta = (
                        datetime.utcnow()
                        + timedelta(minutes=bloqueo)
                    )

                    flash(
                        f'Cuenta bloqueada durante {bloqueo} minutos',
                        'warning'
                    )

                db.session.commit()

        registro = AuditoriaLogin(
            usuario=username,
            ip=request.remote_addr,
            exito=False
        )

        db.session.add(registro)

        db.session.commit()

        flash(
            'Usuario o contraseña incorrectos',
            'danger'
        )

    return render_template(
        'auth/login.html'
    )

@auth_bp.route('/logout')
@login_required
def logout():

    logout_user()

    return redirect(
        url_for('auth.login')
    )