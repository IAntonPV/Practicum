from flask import Blueprint, request, jsonify
from datetime import datetime

from app.models import ProjectMember, Task, BoardList, Project
from app.services import (
    ProjectService, BoardListService, TaskService, ProjectMemberService
)

api_blueprint = Blueprint('api', __name__)


@api_blueprint.route('/projects', methods=['GET', 'POST'])
def projects():
    if request.method == 'GET':
        projects = ProjectService.get_projects()
        return jsonify([{
            'id': p.id,
            'name': p.name,
            'description': p.description,
            'created_at': p.created_at.isoformat()
        } for p in projects])

    elif request.method == 'POST':
        data = request.get_json()
        project = ProjectService.create_project(
            name=data['name'],
            description=data.get('description')
        )
        return jsonify({
            'id': project.id,
            'name': project.name,
            'description': project.description
        }), 201


@api_blueprint.route('/projects/<int:project_id>', methods=['GET', 'PUT', 'DELETE'])
def project_detail(project_id):
    if request.method == 'GET':
        project = Project.query.get_or_404(project_id)
        return jsonify({
            'id': project.id,
            'name': project.name,
            'description': project.description,
            'created_at': project.created_at.isoformat(),
            'updated_at': project.updated_at.isoformat()
        })

    elif request.method == 'PUT':
        data = request.get_json()
        project = ProjectService.update_project(
            project_id=project_id,
            name=data.get('name'),
            description=data.get('description')
        )
        return jsonify({
            'id': project.id,
            'name': project.name,
            'description': project.description
        })

    elif request.method == 'DELETE':
        ProjectService.delete_project(project_id)
        return '', 204


@api_blueprint.route('/projects/<int:project_id>/lists', methods=['GET', 'POST'])
def board_lists(project_id):
    if request.method == 'GET':
        lists = BoardListService.get_lists(project_id)
        return jsonify([{
            'id': l.id,
            'name': l.name,
            'position': l.position,
            'project_id': l.project_id
        } for l in lists])

    elif request.method == 'POST':
        data = request.get_json()
        board_list = BoardListService.create_list(
            project_id=project_id,
            name=data['name'],
            position=data.get('position')
        )
        return jsonify({
            'id': board_list.id,
            'name': board_list.name,
            'position': board_list.position
        }), 201


@api_blueprint.route('/lists/<int:list_id>', methods=['GET', 'PUT', 'DELETE'])
def board_list_detail(list_id):
    if request.method == 'GET':
        board_list = BoardList.query.get_or_404(list_id)
        return jsonify({
            'id': board_list.id,
            'name': board_list.name,
            'position': board_list.position,
            'project_id': board_list.project_id
        })

    elif request.method == 'PUT':
        data = request.get_json()
        board_list = BoardListService.update_list(
            list_id=list_id,
            name=data.get('name'),
            position=data.get('position')
        )
        return jsonify({
            'id': board_list.id,
            'name': board_list.name,
            'position': board_list.position
        })

    elif request.method == 'DELETE':
        BoardListService.delete_list(list_id)
        return '', 204


@api_blueprint.route('/lists/<int:list_id>/tasks', methods=['GET', 'POST'])
def tasks(list_id):
    if request.method == 'GET':
        # Parse filters
        filter_args = {}
        if 'created_after' in request.args:
            try:
                filter_args['created_after'] = datetime.fromisoformat(request.args['created_after'])
            except ValueError:
                pass

        tasks = TaskService.get_tasks(list_id, filter_args)
        return jsonify([{
            'id': t.id,
            'title': t.title,
            'description': t.description,
            'position': t.position,
            'list_id': t.list_id,
            'created_at': t.created_at.isoformat(),
            'updated_at': t.updated_at.isoformat()
        } for t in tasks])

    elif request.method == 'POST':
        data = request.get_json()
        task = TaskService.create_task(
            list_id=list_id,
            title=data['title'],
            description=data.get('description'),
            position=data.get('position')
        )
        return jsonify({
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'position': task.position
        }), 201


@api_blueprint.route('/tasks/<int:task_id>', methods=['GET', 'PUT', 'DELETE'])
def task_detail(task_id):
    if request.method == 'GET':
        task = Task.query.get_or_404(task_id)
        return jsonify({
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'position': task.position,
            'list_id': task.list_id,
            'created_at': task.created_at.isoformat(),
            'updated_at': task.updated_at.isoformat()
        })

    elif request.method == 'PUT':
        data = request.get_json()
        task = TaskService.update_task(
            task_id=task_id,
            title=data.get('title'),
            description=data.get('description'),
            list_id=data.get('list_id'),
            position=data.get('position')
        )
        return jsonify({
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'position': task.position,
            'list_id': task.list_id
        })

    elif request.method == 'DELETE':
        TaskService.delete_task(task_id)
        return '', 204


@api_blueprint.route('/tasks/<int:task_id>/logs', methods=['GET'])
def task_logs(task_id):
    logs = TaskService.get_task_logs(task_id)
    return jsonify([{
        'id': l.id,
        'message': l.message,
        'created_at': l.created_at.isoformat()
    } for l in logs])


@api_blueprint.route('/projects/<int:project_id>/members', methods=['GET', 'POST', 'DELETE'])
def project_members(project_id):
    if request.method == 'GET':
        members = ProjectMember.query.filter_by(project_id=project_id).all()
        return jsonify([{
            'id': m.id,
            'user_id': m.user_id,
            'joined_at': m.joined_at.isoformat()
        } for m in members])

    elif request.method == 'POST':
        data = request.get_json()
        member = ProjectMemberService.add_member(
            project_id=project_id,
            user_id=data['user_id']
        )
        return jsonify({
            'id': member.id,
            'user_id': member.user_id,
            'joined_at': member.joined_at.isoformat()
        }), 201

    elif request.method == 'DELETE':
        data = request.get_json()
        ProjectMemberService.remove_member(
            project_id=project_id,
            user_id=data['user_id']
        )
        return '', 204