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
from models import db, User, People, Planet, Favorite
import requests
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
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

# @app.route('/user', methods=['GET'])
# def handle_hello():

#     response_body = {
#         "msg": "Hello, this is your GET /user response "
#     }

#     return jsonify(response_body), 200


@app.route('/people', methods=['GET'])
def get_people():
    people = People.query.all()
    return jsonify([item.serialize() for item in people]), 200

@app.route('/people/<int:people_id>', methods=['GET'])
def get_one_people(people_id):
    person = People.query.get(people_id)

    if person is None:
        return jsonify({'error': 'user not found'}), 404

    else:
        return jsonify(person.serialize()), 200

@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    return jsonify([item.serialize() for item in planets]), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_one_planet(planet_id):
    planet = Planet.query.get(planet_id)

    if planet is None:
        return jsonify({'error': 'planet not found'}), 404

    else:
        return jsonify(planet.serialize()), 200
    

@app.route("/users", methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.serialize() for user in users]), 200

@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    user_id = 8

    if user_id is None:
        return jsonify({'error': 'user_id es necesario'}), 400
    
    favorites = Favorite.query.filter_by(user_id=user_id).all()
    return jsonify([favorite.serialize() for favorite in favorites]), 200


@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    body = request.get_json()
    user_id = body.get('user_id')

    if user_id is None:
        return jsonify({'error': 'user_id es necesario'}), 400
    
    
    try:
        favorite = Favorite(user_id=user_id, planet_id=planet_id)
        db.session.add(favorite)
        db.session.commit()
        return jsonify({'msg': 'Planet saved'}), 201
    
    except Exception as error:
        db.session.rollback()
        return jsonify({'error': f'Ocurrio un error: {str(error)}'}), 500
    

@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_people(people_id):
    body = request.get_json()
    user_id = body.get('user_id')

    if user_id is None:
        return jsonify({'error': 'user_id es necesario'}), 400
    
    try:
        favorite = Favorite(user_id=user_id, people_id=people_id)
        db.session.add(favorite)
        db.session.commit()
        return jsonify({'msg': 'People saved'}), 201
    
    except Exception as error:
        db.session.rollback()
        return jsonify({'error': f'Ocurrio un error: {str(error)}'}), 500
    

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    body = request.get_json()
    user_id = body.get('user_id')

    favorite = Favorite.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    if not favorite:
        return jsonify({'error': "Favorite not found"}), 404
    
    try:
      db.session.delete(favorite)
      db.session.commit()
      return jsonify({'msg': 'Planet deleted'}), 200
    
    except Exception as error:
        db.session.rollback()
        return jsonify({'error': f'Ocurrio un error: {str(error)}'}), 500
    
@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_people(people_id):
    body =request.get_json()
    user_id = body.get('user_id')

    favorite = Favorite.query.filter_by(user_id=user_id, people_id=people_id).first()

    if not favorite:
        return jsonify({'error': 'Not found'}), 404
    
    try:

        db.session.delete(favorite)
        db.session.commit()
        return jsonify({'msg': "People deleted"}), 200
    
    except Exception as error:
        db.session.rollback()
        return jsonify({'error': f'Ocurrio un error: {str(error)}'}), 500
    



@app.route('/people-population', methods=['GET'])
def populate_people():

    URL_PEOPLE = "https://swapi.tech/api/people?page=1&limit=50"
    response = requests.get(URL_PEOPLE)
    data = response.json()
    for person in data['results']:
        response = requests.get(person['url'])
        person_data = response.json()
        person_data = person_data['result']

        people = People()
        people.name = person_data['properties']['name']
        people.description = person_data['description']
        people.eye_color = person_data['properties']['eye_color']

        db.session.add(people)

    try:
        db.session.commit()
        return jsonify("People saved"), 201

    except Exception as error:
        db.session.rollback()
        return jsonify(f'Error: {error.args}')

@app.route("/planet-population",  methods=["GET"])
def populate_planet():

    URL_PLANET = "https://swapi.tech/api/planets?page=1&limit=50"
    response = requests.get(URL_PLANET)
    data = response.json()
    for person in data["results"]:
        response = requests.get(person["url"])
        person_data = response.json()
        person_data = person_data["result"]

        planet = Planet()
        planet.name = person_data["properties"]["name"]
        planet.description = person_data["description"]
        # people.eye_color = person_data["properties"]["eye_color"]

        db.session.add(planet)

    try:
        db.session.commit()
        return jsonify("Planet saved"), 201

    except Exception as error:
        db.session.rollback()
        return jsonify(f"Error: {error.args}")


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)