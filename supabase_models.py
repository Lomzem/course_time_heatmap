import datetime
from typing import List, Optional

from sqlalchemy import (
    Enum,
    ForeignKeyConstraint,
    Integer,
    PrimaryKeyConstraint,
    Text,
    Time,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import enum


class instructionModeEnum(enum.Enum):
    virtual = "virtual"
    inperson = "inperson"

class Base(DeclarativeBase):
    pass


class Major(Base):
    __tablename__ = "Major"
    __table_args__ = (PrimaryKeyConstraint("id", name="Major_pkey"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(Text)

    Course: Mapped[List["Course"]] = relationship("Course", back_populates="Major_")


class Term(Base):
    __tablename__ = "Term"
    __table_args__ = (PrimaryKeyConstraint("id", name="Term_pkey"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(Text)

    Session: Mapped[List["Session"]] = relationship("Session", back_populates="Term_")


class TimeSlot(Base):
    __tablename__ = "TimeSlot"
    __table_args__ = (PrimaryKeyConstraint("id", name="TimeSlot_pkey"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    time: Mapped[Optional[datetime.time]] = mapped_column(Time)

    Occupancy: Mapped[List["Occupancy"]] = relationship(
        "Occupancy", back_populates="TimeSlot_"
    )


class Weekday(Base):
    __tablename__ = "Weekday"
    __table_args__ = (PrimaryKeyConstraint("id", name="Weekday_pkey"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(Text)

    Occupancy: Mapped[List["Occupancy"]] = relationship(
        "Occupancy", back_populates="Weekday_"
    )


class Course(Base):
    __tablename__ = "Course"
    __table_args__ = (
        ForeignKeyConstraint(
            ["majorId"], ["Major.id"], name="Course_majorId_Major_id_fk"
        ),
        PrimaryKeyConstraint("id", name="Course_pkey"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    majorId: Mapped[Optional[int]] = mapped_column(Integer)

    Major_: Mapped[Optional["Major"]] = relationship("Major", back_populates="Course")
    Session: Mapped[List["Session"]] = relationship("Session", back_populates="Course_")


class Session(Base):
    __tablename__ = "Session"
    __table_args__ = (
        ForeignKeyConstraint(
            ["courseId"], ["Course.id"], name="Session_courseId_Course_id_fk"
        ),
        ForeignKeyConstraint(["termId"], ["Term.id"], name="Session_termId_Term_id_fk"),
        PrimaryKeyConstraint("id", name="Session_pkey"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    courseId: Mapped[Optional[int]] = mapped_column(Integer)
    termId: Mapped[Optional[int]] = mapped_column(Integer)
    classSection: Mapped[Optional[int]] = mapped_column(Integer)
    instructionMode: Mapped[Optional[str]] = mapped_column(
        Enum("virtual", "inperson", name="instructionMode")
    )

    Course_: Mapped[Optional["Course"]] = relationship(
        "Course", back_populates="Session"
    )
    Term_: Mapped[Optional["Term"]] = relationship("Term", back_populates="Session")
    Occupancy: Mapped[List["Occupancy"]] = relationship(
        "Occupancy", back_populates="Session_"
    )


class Occupancy(Base):
    __tablename__ = "Occupancy"
    __table_args__ = (
        ForeignKeyConstraint(
            ["sessionId"], ["Session.id"], name="Occupancy_sessionId_Session_id_fk"
        ),
        ForeignKeyConstraint(
            ["timeSlotId"], ["TimeSlot.id"], name="Occupancy_timeSlotId_TimeSlot_id_fk"
        ),
        ForeignKeyConstraint(
            ["weekdayId"], ["Weekday.id"], name="Occupancy_weekdayId_Weekday_id_fk"
        ),
        PrimaryKeyConstraint("id", name="Occupancy_pkey"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sessionId: Mapped[Optional[int]] = mapped_column(Integer)
    weekdayId: Mapped[Optional[int]] = mapped_column(Integer)
    timeSlotId: Mapped[Optional[int]] = mapped_column(Integer)
    studentCount: Mapped[Optional[int]] = mapped_column(Integer)

    Session_: Mapped[Optional["Session"]] = relationship(
        "Session", back_populates="Occupancy"
    )
    TimeSlot_: Mapped[Optional["TimeSlot"]] = relationship(
        "TimeSlot", back_populates="Occupancy"
    )
    Weekday_: Mapped[Optional["Weekday"]] = relationship(
        "Weekday", back_populates="Occupancy"
    )
