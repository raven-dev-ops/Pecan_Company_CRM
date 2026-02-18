from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, sessionmaker

from pecan_crm.db.models import Customer


@dataclass(frozen=True)
class CustomerInput:
    first_name: str
    last_name: str
    phone: str
    email: str
    notes: str
    is_active: bool = True


class CustomerRepository:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self.session_factory = session_factory

    def list_customers(self, *, include_inactive: bool = True, search: str = "") -> list[Customer]:
        with self.session_factory() as session:
            query = select(Customer)
            if not include_inactive:
                query = query.where(Customer.is_active.is_(True))
            if search:
                wildcard = f"%{search.strip()}%"
                query = query.where(
                    or_(
                        Customer.first_name.ilike(wildcard),
                        Customer.last_name.ilike(wildcard),
                        Customer.phone.ilike(wildcard),
                        Customer.email.ilike(wildcard),
                    )
                )
            query = query.order_by(Customer.last_name.asc(), Customer.first_name.asc())
            return list(session.scalars(query).all())

    def find_likely_duplicates(
        self,
        *,
        phone: str,
        email: str,
        first_name: str,
        last_name: str,
        exclude_customer_id: int | None = None,
    ) -> list[Customer]:
        with self.session_factory() as session:
            clauses = []
            if phone.strip():
                clauses.append(Customer.phone == phone.strip())
            if email.strip():
                clauses.append(func.lower(Customer.email) == email.strip().lower())
            if first_name.strip() and last_name.strip():
                clauses.append(
                    (func.lower(Customer.first_name) == first_name.strip().lower())
                    & (func.lower(Customer.last_name) == last_name.strip().lower())
                )

            if not clauses:
                return []

            query = select(Customer).where(or_(*clauses))
            if exclude_customer_id is not None:
                query = query.where(Customer.customer_id != exclude_customer_id)

            return list(session.scalars(query).all())

    def save(self, data: CustomerInput, *, customer_id: int | None = None) -> Customer:
        with self.session_factory() as session:
            if customer_id is None:
                entity = Customer(
                    first_name=data.first_name or None,
                    last_name=data.last_name or None,
                    phone=data.phone or None,
                    email=data.email or None,
                    notes=data.notes or None,
                    is_active=data.is_active,
                )
                session.add(entity)
            else:
                entity = session.get(Customer, customer_id)
                if entity is None:
                    raise ValueError("Customer not found")
                entity.first_name = data.first_name or None
                entity.last_name = data.last_name or None
                entity.phone = data.phone or None
                entity.email = data.email or None
                entity.notes = data.notes or None
                entity.is_active = data.is_active
                entity.updated_at_utc = datetime.utcnow()

            session.commit()
            session.refresh(entity)
            return entity