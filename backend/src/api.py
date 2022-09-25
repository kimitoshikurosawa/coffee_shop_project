import os
import sys

from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
# db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks", methods=['GET'])
def retrieve_drinks():
    try:
        error = False
        short_drinks = [drink.short() for drink in Drink.query.all()]
    except:
        error = True
        print(sys.exc_info())
    if error:
        abort(400)
    else:
        return jsonify({
            'success': True,
            'drinks': short_drinks,
        })


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks-detail", methods=['GET'])
@requires_auth('get:drinks-detail')
def retrieve_drinks_details(jwt):
    try:
        error = False
        long_drinks = [drink.long() for drink in Drink.query.all()]
    except:
        error = True
        print(sys.exc_info())
    if error:
        abort(400)
    else:
        return jsonify({
            'success': True,
            'drinks': long_drinks,
        })


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks", methods=['POST'])
@requires_auth('post:drinks')
def create_drinks(jwt):
    try:
        body = request.get_json()
        error = False
        title = body.get("title")
        recipe = body.get("recipe")
        drink = Drink(title=title,
                      recipe=json.dumps(recipe))
        drink.insert()
        created_drink = drink.long()

    except:
        error = True
        print(sys.exc_info())

    if error:
        abort(400)
    else:
        return jsonify({
            'success': True,
            'drinks': created_drink,
        })


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks/<drink_id>", methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_drink(jwt, drink_id):
    error = False
    if not drink_id:
        abort(404)

    try:
        data = request.get_json()
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
        drink.title = data['title']
        drink.recipe = json.dumps(data['recipe'])
        drink.update()
        updated_drink = drink.long()
    except:
        error = True
        print(sys.exc_info())
    if error:
        abort(400)
    else:
        return jsonify({
            'success': True,
            'drinks': updated_drink,
        })


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks/<drink_id>", methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt, drink_id):
    drink = Drink.query.filter_by(id=drink_id).one_or_none()
    try:
        if drink is None:
            abort(404)
        drink.delete()
        return jsonify({
            "success": True,
            "deleted": drink.long()
        })
    except:
        abort(422)


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''


@app.errorhandler(500)
def server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "Internal Server Error"
    }), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(422)
def unprocessable_entity(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable action"
    }), 422


@app.errorhandler(405)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "Method not allow"
    }), 405


@app.errorhandler(400)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Bad Request"
    }), 400


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''


@app.errorhandler(AuthError)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": str(error)
    }), 401
