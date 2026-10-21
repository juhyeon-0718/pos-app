"""auth 모듈의 DB 접근 계층. users/tables 테이블만 다룬다 (D-25)."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.models import Table, User


def get_user_by_username(db: Session, username: str) -> User | None:
    return db.execute(select(User).where(User.username == username)).scalar_one_or_none()


def get_user_by_id(db: Session, user_id: str) -> User | None:
    return db.get(User, user_id)


def list_users(db: Session) -> list[User]:
    return list(db.execute(select(User).order_by(User.created_at)).scalars().all())


def count_users_by_role(db: Session, role: str) -> int:
    return len(db.execute(select(User.id).where(User.role == role)).all())


def create_user(db: Session, *, username: str, password_hash: str, role: str) -> User:
    user = User(username=username, password_hash=password_hash, role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user: User, **fields) -> User:
    for key, value in fields.items():
        if value is not None:
            setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user


def get_table_by_id(db: Session, table_id: str) -> Table | None:
    return db.get(Table, table_id)


def list_tables(db: Session) -> list[Table]:
    return list(db.execute(select(Table).order_by(Table.table_no)).scalars().all())


def get_table_numbers(db: Session, table_ids: list[str]) -> dict[str, int]:
    if not table_ids:
        return {}
    rows = db.execute(select(Table.id, Table.table_no).where(Table.id.in_(table_ids))).all()
    return {table_id: table_no for table_id, table_no in rows}


def create_table(db: Session, *, table_no: int) -> Table:
    table = Table(table_no=table_no)
    db.add(table)
    db.commit()
    db.refresh(table)
    return table


def reissue_qr(db: Session, table: Table) -> Table:
    from app.models.base import gen_id, utcnow

    table.qr_token = gen_id("qr")
    table.qr_issued_at = utcnow()
    db.commit()
    db.refresh(table)
    return table
