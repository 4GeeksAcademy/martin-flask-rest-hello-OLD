"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for,session
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User,People,Planet,FavoritePlanet,FavoritePeople
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

@app.route('/users', methods=['GET'])
def get_users():
    all_users= User.query.all()
    results = list(map(lambda user: user.serialize(),all_users))

    response_body = {
        "msg": "Hello, this is your GET /user response ",
        "users": results
    }

    return jsonify(response_body), 200


@app.route('/people', methods=['GET'])
def get_character():
    all_characters= People.query.all()
    results = list(map(lambda character: character.serialize(),all_characters))


    response_body = {
        "msg": "Hello, this is your GET /people response ",
        "characters": results
    }

    return jsonify(response_body), 200

@app.route('/people/<int:character_id>', methods=['GET'])
def get_one_character(character_id):
    one_character= People.query.get(character_id)
    

    return jsonify(one_character.serialize()), 200



@app.route('/planets', methods=['GET'])
def get_planets():
    all_planets= Planet.query.all()
    results = list(map(lambda planet: planet.serialize(),all_planets))


    response_body = {
        "msg": "Hello, this is your GET /planet response ",
        "planets": results
    }

    return jsonify(response_body), 200


@app.route('/planet/<int:planet_id>', methods=['GET'])
def get_one_planet(planet_id):
        one_planet= Planet.query.get(planet_id)
    

        return jsonify(one_planet.serialize()), 200
@app.route('/planet', methods=['POST'])
def add_planet():
    body= request.get_json()
    
    planet = Planet(name =body["name"], population=body["population"],
                           terrain = body["terrain"], climate =body["climate"])
    db.session.add(planet)
    db.session.commit()
    return "planet created"
@app.route('/user/favorites', methods=['GET'])
def get_user_favorites():
    favorite_chars = FavoritePeople.query.all()
    favorite_planets = FavoritePlanet.query.all()
    char_fav_list = list(map(lambda fav: fav.serialize(),favorite_chars))
    planet_fav_list = list(map(lambda fav: fav.serialize(),favorite_planets))
    

    
    response_body = {
        "msg": "User favorite List",
        "favorite_planets": planet_fav_list,
        "favorite_characters": char_fav_list
    }
    return jsonify(response_body), 200


@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    first_user = User.query.first()
    user_id = first_user.id
    
    new_favorite = FavoritePlanet(user_id= user_id, planet_id=planet_id)
    db.session.add(new_favorite)
    db.session.commit()
    return "favorite planet created"
@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_character(people_id):
    first_user = User.query.first()
    user_id = first_user.id
    
    new_favorite = FavoritePeople(user_id= user_id, people_id=people_id)
    db.session.add(new_favorite)
    db.session.commit()
    return " favorite character created"
@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    planet_fav = FavoritePlanet.query.get(planet_id)
    db.session.delete(planet_fav)
    db.session.commit()

    response_body ={
        "msg": "Favorite Planet Deleted"
    }
    return response_body, 200
@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_char(people_id):
    character_fav = FavoritePeople.query.get(people_id)
    db.session.delete(character_fav)
    db.session.commit()

    response_body ={
        "msg": "Favorite Character Deleted"
    }
    return response_body, 200



        

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
