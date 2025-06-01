import uuid

from sqlalchemy import Boolean, Column, Date, ForeignKey, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class SubmissionRuleDrug(Base):
    __tablename__ = 'submission_rule_drug'

    submission_rule_id = Column(
        UUID(as_uuid=True),
        ForeignKey('submission_rules.id'),
        primary_key=True
    )
    drug_id = Column(
        UUID(as_uuid=True),
        ForeignKey('drugs.id'),
        primary_key=True
    )

    submission_rule = relationship("SubmissionRule")
    drug = relationship("Drug")


class Drug(Base):
    __tablename__ = "drugs"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    trade_name = Column(String, nullable=False)
    inn = Column(String, nullable=True, default=None)
    obligation = Column(String, nullable=True)
    release_forms = Column(String, nullable=True)

    submission_rules = relationship(
        "SubmissionRule",
        secondary=lambda: SubmissionRuleDrug.__table__,
        back_populates="drugs"
    )

    def __str__(self):
        return f"Drug: {self.id}, {self.trade_name[:30]} {self.inn[:30]}"


class TypeOfEvent(Base):
    __tablename__ = "type_of_event"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    name = Column(String, nullable=True)

    submission_rule = relationship(
        "SubmissionRule", back_populates="event_types"
    )

    def __str__(self):
        return f"type_of_event: {self.id}, {self.name}"


class SubmissionRule(Base):
    __tablename__ = "submission_rules"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )

    source_countries = Column(String, nullable=True)
    receiver = Column(String, nullable=True)
    deadline_to_submit = Column(Date, nullable=True)
    format = Column(String, nullable=True)
    other_procedures = Column(String, nullable=True)
    type_of_event = Column(UUID, ForeignKey("type_of_event.id"), nullable=True)
    valid_start_date = Column(DateTime, nullable=True, default=None)
    valid_end_date = Column(DateTime, nullable=True, default=None)

    drugs = relationship(
        "Drug",
        secondary=lambda: SubmissionRuleDrug.__table__,
        back_populates="submission_rules"
    )
    event_types = relationship("TypeOfEvent", back_populates="submission_rule")

    def __str__(self):
        return f"SubmissionRule: {self.id}, {self.receiver[:30]}"


class User(Base):
    __tablename__ = "user"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    is_admin = Column(Boolean, nullable=False, default=False)
