from app import create_app, db, create_admin_user
from flask_migrate import Migrate

app = create_app()
migrate = Migrate(app, db)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_admin_user()

    app.run(debug=True)
