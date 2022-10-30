from tasksapp.tasks.resource import TasksResource


def tasks_routes(api):
    api.add_resource(TasksResource, '/api/tasks', '/api/tasks/<int:task_id>')
    
