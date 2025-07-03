from app import app, db # Asegurate que esto apunta a tu instancia Flask
from models import  User, Planets, People


def run_seeder():
    with app.app_context():
        db.drop_all()
        db.create_all()

        # Crear usuarios
        user1 = User(email="luke@jedi.com",
                     password="force123", is_active=True)
        user2 = User(email="leia@organa.com",
                     password="alderaan", is_active=True)

        # Crear planetas
        planet1 = Planets(name="Tatooine")
        planet2 = Planets(name="Dagobah")
        planet3 = Planets(name="Alderaan")

        # Crear personajes
        person1 = People(name="Luke Skywalker")
        person2 = People(name="Leia Organa")
        person3 = People(name="Yoda")

        # Agregar todo
        db.session.add_all([user1, user2, planet1, planet2,
                           planet3, person1, person2, person3])
        db.session.commit()

        print("✅ Base de datos poblada con éxito.")


if __name__ == "__main__":
    run_seeder()
