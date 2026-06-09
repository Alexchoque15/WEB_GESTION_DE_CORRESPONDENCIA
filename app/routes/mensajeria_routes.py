from flask import Blueprint
from flask import render_template

from flask_login import login_required

from app.utils.roles import rol_requerido


mensajeria_bp = Blueprint(
    'mensajeria',
    __name__,
    url_prefix='/mensajeria'
)


@mensajeria_bp.route('/')
@login_required
@rol_requerido(
    'ADMINISTRADOR',
    'MENSAJERIA'
)
def index():

    return render_template(
        'mensajeria/index.html'
    )