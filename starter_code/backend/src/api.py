from crypt import methods
import os, sys
from resource import prlimit
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
@TODO uncomment the following line to initialize the database
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
@app.route('/drinks')
def get_drinks():
    try:
        collection = Drink.query.all()
        
        drinks = [col.short() for col in collection]
        
        return jsonify(
            {
                "success": True,
                "drinks": drinks,
            }
        ), 200
    except:
        abort(500)

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_single_drink(payload):
    try:
        selection = Drink.query.all()
        drinks = [col.long() for col in selection]
            
        return jsonify(
            {
                "success": True,
                "drinks": drinks,
            }
        ), 200
    except:
        abort(500)
    
'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create(payload):
    try:
        body = request.get_json()
        title = body['title']
        recipe = body['recipe']
        
        check_title = Drink.query.filter(Drink.title == title).one_or_none()
        if check_title and check_title.short()['title']:
            abort(400)
            
        selection = Drink(title=title, recipe=recipe)
        selection.insert()
        drink = [selection.long()]
        
        return jsonify(
            {
                "success": True,
                "drinks": drink,
            }
        ), 200
    except:
        abort(400)


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
@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update(payload, id):
    try:
        body = request.get_json()
        title = body['title']
        
        selection = Drink.query.filter(Drink.id == id).one_or_none()
        if not selection:
            abort(404)
            
        selection.title = title
        selection.update()
        drink = [selection.long()]
        
        return (jsonify(
            {
                "success": True,
                "drinks": drink,
            }
        ), 200)
    except:
        # print(sys.exc_info())
        abort(422)
    return None


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
@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def remove(payload, id):
    try:
        drink = Drink.query.get(id)
        if not drink:
            abort(404)
        
        drink.delete()
    except:
        abort(422)
    
    return jsonify(
        {
            "success": True,
            "delete": id,
        }
    ), 200


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

@app.errorhandler(400)
def bad_request(error):
    return jsonify({"success": False, "error": 400, "message": "bad request"}), 400

@app.errorhandler(405)
def not_found(error):
    return (
        jsonify({"success": False, "error": 405, "message": "method not allowed"}),
        405,
    )

@app.errorhandler(500)
def server_error(error):
    return (
        jsonify({"success": False, "error": 500, "message": "server error"}),
        500,
    )

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def not_found(error):
    return (
        jsonify({"success": False, "error": 404, "message": "resource not found"}),
        404,
    )


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def unauthorized(error):
    statusCode = error.status_code
    message = [x for x in error.args][0]['description']
    code = [x for x in error.args][0]['code']
    return (
        jsonify({"success": False, "error": code, "message": message, "statusCode": statusCode}),
        statusCode,
    )
