from tasksapp.models import User
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource, reqparse
from tasksapp.schemas.app_schemas import UserSchema
from datetime import datetime


user_schema = UserSchema()
users_schema = UserSchema(many=True)

class Users(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()

    # http method: get
    @jwt_required()
    def get(self, user_id=None):
        if user_id:
            if not user_id == get_jwt_identity():
                return {"message": "You can only view your profile"}, 403
            # get a single user
            user = User.query.filter_by(id=user_id).first()
            if not user:
                return {'message': 'User with id {} does not exist'.format(user_id)}, 404

            return user_schema.dump(user), 200
        
        
        # get all users
        users = User.query.all()
        return users_schema.dump(users), 200

    
    @jwt_required()
    def put(self, user_id):
        # While updating user information, all fields are optional
        self.parser.add_argument('name', type=str)
        self.parser.add_argument('email', type=str)
        self.parser.add_argument('password', type=str)
        
        user = User.get_user_by_id(user_id)

        if not user:
            return {'message': 'User not found'}, 404

        data = self.parser.parse_args()

        # update user 
        user.name = data['name'] if data['name'] else user.name
        user.email = data['email'] if data['email'] else user.email
        # user.date_created = datetime.strptime(data['date_created'], '%Y-%m-%d') if data['date_created'] else user.date_created
        user.update()

        # return updated user
        return user_schema.dump(user), 200


    @jwt_required()
    def delete(self, user_id):
        user = User.get_user_by_id(user_id)

        if not user:
            return {'message': 'User not found'}, 404

        # check for ownership
        if user.created_by != get_jwt_identity():
            return {'message': 'You are not authorized to delete this user'}, 401

        user.delete()
        return {'message': 'User deleted successfully'}, 200
