from werkzeug.security import generate_password_hash

from app import create_app, db
from app.models.usuario import Usuario

app = create_app()

with app.app_context():

    usuarios = [

        {
            "usuario":"recepcion",
            "correo":"recepcion@correo.com",
            "rol":"RECEPCION",
            "rol_id":2
        },

        {
            "usuario":"personal",
            "correo":"personal@correo.com",
            "rol":"PERSONAL",
            "rol_id":3
        },

        {
            "usuario":"mensajeria",
            "correo":"mensajeria@correo.com",
            "rol":"MENSAJERIA",
            "rol_id":4
        },

        {
            "usuario":"archivo",
            "correo":"archivo@correo.com",
            "rol":"ARCHIVO",
            "rol_id":5
        }

    ]

    for u in usuarios:

        existe = Usuario.query.filter_by(
            usuario=u["usuario"]
        ).first()

        if not existe:

            nuevo = Usuario(

                nombres=u["usuario"].capitalize(),

                apellidos="Sistema",

                usuario=u["usuario"],

                correo=u["correo"],

                password=generate_password_hash(
                    "123456"
                ),

                rol=u["rol"],

                rol_id=u["rol_id"]

            )

            db.session.add(nuevo)

    db.session.commit()

    print("Usuarios creados")