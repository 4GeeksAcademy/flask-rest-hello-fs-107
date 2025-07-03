"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planets, People, Favorites
from sqlalchemy import select
# from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints


@app.route('/')
def sitemap():
    return generate_sitemap(app)


# Usuarios
@app.route("/users", methods=["GET"])
def handle_user():
    users = User.query.all()
    return jsonify([p.serialize() for p in users]), 200
# traer favoritos de un usuario


@app.route("/users/<int:user_id>/favorites", methods=["GET"])
def handle_user_favorites(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404
    return jsonify([p.serialize() for p in user.favoritos]), 200


# crear favoritos de un usuario:
@app.route("/users/<int:user_id>/favorites", methods=["POST"])
def add_favorite(user_id):
    body = request.get_json()
    if not body:
        return jsonify({"msg": "No data provided"}), 400

    typeof = body.get("typeof")
    reference_id = body.get("reference_id")

    if typeof not in ["planets", "people"]:
        return jsonify({"msg": "Invalid type"}), 400
    if not reference_id:
        return jsonify({"msg": "reference_id is required"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404

    # Verifica que el objeto referenciado exista
    if typeof == "planets":
        ref = Planets.query.get(reference_id)
    else:
        ref = People.query.get(reference_id)
    if not ref:
        return jsonify({"msg": f"{typeof.title()} not found"}), 404

    # Crea el favorito
    new_fav = Favorites(user_id=user_id, typeof=typeof,
                        reference_id=reference_id)
    db.session.add(new_fav)
    db.session.commit()
    return jsonify(new_fav.id), 201

# eliminar favoritos de un usuario:


@app.route("/users/<int:user_id>/favorites/<int:favorite_id>", methods=["DELETE"])
def delete_favorite(user_id, favorite_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404

    favorite = Favorites.query.filter_by(
        id=favorite_id, user_id=user_id).first()
    if not favorite:
        return jsonify({"msg": "Favorite not found"}), 404

    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"msg": "Favorite deleted"}), 200

# Planets


@app.route("/planets", methods=["GET"])
def handle_planets():
    planets = Planets.query.all()
    return jsonify([p.serialize() for p in planets]), 200
# traer uno Con ID


@app.route("/planets/<int:planet_id>", methods=["GET"])
def handle_single_planet(planet_id):
    single = Planets.query.get(planet_id)
    if not single:
        return jsonify({"msg": "Planet not found"}), 404
    return jsonify(single.serialize()), 200

# People


@app.route("/people", methods=["GET"])
def handle_people():
    people = People.query.all()
    return jsonify([p.serialize() for p in people]), 200

# traer uno Con ID


@app.route("/people/<int:people_id>", methods=["GET"])
def handle_single(people_id):
    single = People.query.get(people_id)
    if not single:
        return jsonify({"msg": "Person not found"}), 404
    return jsonify(single.serialize()), 200

# Crear personaje


@app.route("/people", methods=["POST"])
def handle_people_post():
    body = request.get_json()
    if not body:
        return jsonify({"msg": "No data provided"}), 400
    new_person = People(
        name=body.get("name"),
    )
    db.session.add(new_person)
    db.session.commit()
    return jsonify(new_person.serialize()), 201


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
