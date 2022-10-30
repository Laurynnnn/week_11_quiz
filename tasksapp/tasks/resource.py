from datetime import datetime
from tasksapp.models import Task
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource, reqparse

from tasksapp.schemas.app_schemas import TaskSchema

task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)

# Tasks Resource
class TasksResource(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()

    @jwt_required()
    def post(self):
        self.parser.add_argument('title', type=str, required=True, help='Title cannot be blank')
        self.parser.add_argument('description', type=str, required=True, help='Description cannot be blank')
        self.parser.add_argument('due_date', type=str, required=True, help='Due date cannot be blank')

        data = self.parser.parse_args()

        # create date object from string => needed by sqlite db
        data['due_date'] = datetime.strptime(data['due_date'], '%Y-%m-%d')

        user_id = get_jwt_identity()

        new_task = Task(**data, created_by=user_id)
        new_task.save()
        return {'message': 'Task created successfully'}, 201

    @jwt_required()
    def get(self, task_id=None):
        if task_id:
            task = Task.get_task_by_id(task_id)
            if task:
                return task_schema.dump(task), 200
            return {'message': 'Task not found'}, 404

        user_id = get_jwt_identity()
        user_tasks = Task.get_user_tasks(user_id)
        return tasks_schema.dump(user_tasks), 200

    
    @jwt_required()
    def put(self, task_id):
        # While updating a task, all fields are optional
        self.parser.add_argument('title', type=str)
        self.parser.add_argument('description', type=str)
        self.parser.add_argument('due_date', type=str)
        self.parser.add_argument('complete', type=bool)
        
        task = Task.get_task_by_id(task_id)

        if not task:
            return {'message': 'Task not found'}, 404

        # check for ownership
        if task.created_by != get_jwt_identity():
            return {'message': 'You are not authorized to update this task'}, 401

        data = self.parser.parse_args()

        # update task if there is new data else keep the old data
        task.title = data['title'] if data['title'] else task.title
        task.description = data['description'] if data['description'] else task.description
        task.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d') if data['due_date'] else task.due_date
        task.complete = data['complete'] if data['complete'] else task.complete
        task.update()

        # return updated task
        return task_schema.dump(task), 200


    @jwt_required()
    def delete(self, task_id):
        task = Task.get_task_by_id(task_id)

        if not task:
            return {'message': 'Task not found'}, 404

        # check for ownership
        if task.created_by != get_jwt_identity():
            return {'message': 'You are not authorized to delete this task'}, 401

        task.delete()
        return {'message': 'Task deleted successfully'}, 200

        
