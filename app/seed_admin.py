from werkzeug.security import generate_password_hash

from app import create_app, db
from app.models.usuario import Usuario

app = create_app()

with app.app_context():

    existe = Usuario.query.filter_by(
        usuario='admin'
    ).first()

    if existe:

        print("El administrador ya existe")

    else:

        admin = Usuario(
            nombres="Administrador",
            apellidos="Sistema",
            usuario="admin",
            correo="admin@correo.com",
            rol="ADMINISTRADOR",
            rol_id=1,
            password=generate_password_hash("123456")
        )

        db.session.add(admin)
        db.session.commit()

        print("Administrador creado correctamente")