from datetime import datetime
from app import db
from app.models import Project, BoardList, Task, TaskLog, ProjectMember


class ProjectService:
    @staticmethod
    def create_project(name, description=None):
        try:
            project = Project(name=name, description=description)
            db.session.add(project)
            db.session.flush()  # Получаем ID проекта до коммита

            # Теперь создаем колонки с известным project_id
            default_lists = [
                {'name': 'To Do', 'position': 0},
                {'name': 'In Progress', 'position': 1},
                {'name': 'Done', 'position': 2}
            ]

            for lst in default_lists:
                db.session.add(BoardList(
                    name=lst['name'],
                    position=lst['position'],
                    project_id=project.id  # Используем реальный ID
                ))

            db.session.commit()
            return project
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def get_projects():
        return Project.query.all()

    @staticmethod
    def update_project(project_id, name=None, description=None):
        project = Project.query.get_or_404(project_id)
        if name:
            project.name = name
        if description is not None:
            project.description = description
        db.session.commit()
        return project

    @staticmethod
    def delete_project(project_id):
        project = Project.query.get_or_404(project_id)
        db.session.delete(project)
        db.session.commit()


class BoardListService:
    @staticmethod
    def create_list(project_id, name, position=None):
        project = Project.query.get_or_404(project_id)
        if position is None:
            position = len(project.board_lists)
        board_list = BoardList(name=name, position=position, project_id=project_id)
        db.session.add(board_list)
        db.session.commit()
        return board_list

    @staticmethod
    def get_lists(project_id):
        return BoardList.query.filter_by(project_id=project_id).order_by(BoardList.position).all()

    @staticmethod
    def update_list(list_id, name=None, position=None):
        board_list = BoardList.query.get_or_404(list_id)
        if name:
            board_list.name = name
        if position is not None:
            board_list.position = position
        db.session.commit()
        return board_list

    @staticmethod
    def delete_list(list_id):
        board_list = BoardList.query.get_or_404(list_id)
        db.session.delete(board_list)
        db.session.commit()


class TaskService:
    @staticmethod
    def create_task(list_id, title, description=None, position=None):
        board_list = BoardList.query.get_or_404(list_id)
        if position is None:
            position = len(board_list.tasks)
        task = Task(title=title, description=description, position=position, list_id=list_id)
        db.session.add(task)

        # Create log
        log = TaskLog(message=f'Task created in list "{board_list.name}"', task_id=task.id)
        db.session.add(log)

        db.session.commit()
        return task

    @staticmethod
    def get_tasks(list_id, filter_args=None):
        query = Task.query.filter_by(list_id=list_id)
        if filter_args:
            # Example filter: {'created_after': datetime(2023,1,1)}
            if 'created_after' in filter_args:
                query = query.filter(Task.created_at >= filter_args['created_after'])
            if 'updated_after' in filter_args:
                query = query.filter(Task.updated_at >= filter_args['updated_after'])
        return query.order_by(Task.position).all()

    @staticmethod
    def update_task(task_id, title=None, description=None, list_id=None, position=None):
        task = Task.query.get_or_404(task_id)
        if title:
            task.title = title
        if description is not None:
            task.description = description
        if position is not None:
            task.position = position

        if list_id and list_id != task.list_id:
            old_list = task.list
            new_list = BoardList.query.get_or_404(list_id)
            task.list_id = list_id
            # Create log
            log = TaskLog(
                message=f'Moved from "{old_list.name}" to "{new_list.name}"',
                task_id=task.id
            )
            db.session.add(log)

        db.session.commit()
        return task

    @staticmethod
    def delete_task(task_id):
        task = Task.query.get_or_404(task_id)
        db.session.delete(task)
        db.session.commit()

    @staticmethod
    def get_task_logs(task_id):
        return TaskLog.query.filter_by(task_id=task_id).order_by(TaskLog.created_at.desc()).all()


class ProjectMemberService:
    @staticmethod
    def add_member(project_id, user_id):
        member = ProjectMember.query.filter_by(project_id=project_id, user_id=user_id).first()
        if member:
            return member
        member = ProjectMember(project_id=project_id, user_id=user_id)
        db.session.add(member)
        db.session.commit()
        return member

    @staticmethod
    def remove_member(project_id, user_id):
        member = ProjectMember.query.filter_by(project_id=project_id, user_id=user_id).first_or_404()
        db.session.delete(member)
        db.session.commit()