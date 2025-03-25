from typing import Optional, List, Type

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, joinedload

from database.database import connection
from database.models import Admin, OTPKey, Team, Task, Chain
from page import Page


@connection
def set_otp(session: Session, otp: str) -> Optional[OTPKey]:
    try:
        key = OTPKey(secret=otp)
        session.add(key)
        session.commit()
        return key
    except SQLAlchemyError as e:
        print(f'Error {e}')
        session.rollback()


@connection
def get_otp(session: Session) -> Optional[OTPKey]:
    try:
        return session.query(OTPKey).first()
    except SQLAlchemyError as e:
        print(f'Error {e}')


@connection
def add_admin(session: Session, user_id: int) -> Optional[Admin]:
    try:
        admin = Admin(user_id=user_id)
        session.add(admin)
        session.commit()
        return admin
    except SQLAlchemyError as e:
        print(f'Error {e}')
        session.rollback()


@connection
def get_admin(session: Session, user_id: int) -> Optional[Admin]:
    try:
        return session.get(Admin, user_id)
    except SQLAlchemyError as e:
        print(f'Error {e}')


@connection
def add_team(session: Session, team: Team) -> Optional[Team]:
    try:
        session.add(team)
        session.commit()
        return team
    except SQLAlchemyError as e:
        print(f'Error {e}')
        session.rollback()


@connection
def update_team(
        session: Session,
        team_id: int,
        leader_id: Optional[int] = -1,
        current_chain_order: Optional[int] = None) -> Optional[Team]:
    try:
        team = session.get(Team, team_id)
        if leader_id != -1:
            team.leader_id = leader_id
        if current_chain_order is not None:
            team.current_chain_order = current_chain_order
        session.commit()
        return team
    except SQLAlchemyError as e:
        print(f'Error {e}')
        session.rollback()


@connection
def get_team_by_id(session: Session, team_id: int) -> Optional[Team]:
    try:
        return session.query(Team).options(joinedload(Team.chains)).get(team_id)
    except SQLAlchemyError as e:
        print(f'Error {e}')


@connection
def get_team_by_name(session: Session, team_name: str) -> Optional[Team]:
    try:
        return session.query(Team).filter_by(team_name=team_name).first()
    except SQLAlchemyError as e:
        print(f'Error {e}')


@connection
def get_team_by_leader(session: Session, leader_id: int) -> Optional[Team]:
    try:
        return session.query(Team).filter_by(leader_id=leader_id).first()
    except SQLAlchemyError as e:
        print(f'Error {e}')


@connection
def get_team_by_code(session: Session, code_word: str) -> Optional[Team]:
    try:
        return session.query(Team).filter_by(code_word=code_word).first()
    except SQLAlchemyError as e:
        print(f'Error {e}')


@connection
def get_teams(session: Session, leader_only: bool = False, started_only: bool = False) -> List[Type[Team]]:
    try:
        query = session.query(Team).options(joinedload(Team.chains))
        if leader_only:
            query = query.where(Team.leader_id.isnot(None))
        if started_only:
            query = query.where(Team.current_chain_order > 0)
        teams = query.all()
        return teams
    except SQLAlchemyError as e:
        print(f'Error {e}')
        return []


@connection
def get_teams_paged(session: Session, page: int = 0, limit: int = 10) -> Optional[Page[Team]]:
    try:
        totalCount = session.query(Team).count()
        teams = session.query(Team).options(joinedload(Team.chains)).offset(page * limit).limit(limit)
        return Page(totalCount, page, teams)
    except SQLAlchemyError as e:
        print(f'Error {e}')
        return None


@connection
def add_task(session: Session, task: Task) -> Optional[Task]:
    try:
        session.add(task)
        session.commit()
        return task
    except SQLAlchemyError as e:
        print(f'Error {e}')
        session.rollback()

@connection
def get_task_by_id(session: Session, task_id: int) -> Optional[Task]:
    try:
        return session.query(Task).options(joinedload(Task.chains).joinedload(Chain.team)).get(task_id)
    except SQLAlchemyError as e:
        print(f'Error {e}')

@connection
def get_tasks(session: Session) -> List[Type[Task]]:
    try:
        tasks = session.query(Task).options(joinedload(Task.chains).joinedload(Chain.team)).all()
        return tasks
    except SQLAlchemyError as e:
        print(f'Error {e}')
        return []


@connection
def get_tasks_by_team(session: Session, team_id: int) -> List[Type[Task]]:
    try:
        chains = session.query(Chain).options(joinedload(Chain.task)).filter_by(team_id=team_id).order_by(
            Chain.order).all()
        tasks = list(map(lambda x: x.task, chains))
        return tasks
    except SQLAlchemyError as e:
        print(f'Error {e}')
        session.rollback()
        return []


@connection
def add_chains(session: Session, chains: List[Chain]) -> List[Chain]:
    try:
        session.add_all(chains)
        session.commit()
        return chains
    except SQLAlchemyError as e:
        print(f'Error {e}')
        session.rollback()
        return []


@connection
def get_current_chain(session: Session, team_id: int, order: int) -> Optional[Chain]:
    try:
        return session.query(Chain).options(joinedload(Chain.task)).filter_by(team_id=team_id, order=order).first()
    except SQLAlchemyError as e:
        print(f'Error {e}')


@connection
def delete_chains_by_team(session: Session, team_id: int):
    try:
        session.query(Chain).filter_by(team_id=team_id).delete()
        session.commit()
    except SQLAlchemyError as e:
        print(f'Error {e}')
        session.rollback()
