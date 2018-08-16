from enum import Enum as PyEnum
from sqlalchemy import Column, String, Integer, Enum, DateTime, ForeignKey, text

from base.models import SystemModel, BaseModel


class QuestionDataType(PyEnum):
    CATEGORY = "category"
    STRING = "string"
    DATE = "date"
    GEO = "place"


class Question(SystemModel):
    """
    A question stores a personal question that the user has chosen to answer every time she wants
    to unlock an existing password or generate a new password.
    """

    __tablename__ = "question"

    text = Column(String(40), unique=True, nullable=False)
    password_text = Column(String(40), nullable=False)

    data_type = Column(Enum(QuestionDataType), nullable=False, default=QuestionDataType.STRING)

    # A question may be related to a parent one, for example "date of marriage" is related to "are you married?"
    related_id = Column(Integer, ForeignKey("question.id"), nullable=True)


class Password(BaseModel):
    """
    A source represents the list of the questions that the user has created to unlock or generate passwords.
    """

    __tablename__ = "password"

    name = Column(String(40), nullable=False)


class PasswordQuestion(SystemModel):
    __tablename__ = "password_question"

    password_id = Column(Integer, ForeignKey("password.id"))
    question_id = Column(Integer, ForeignKey("question.id"))

    added_at = Column(DateTime, nullable=False, server_default=text("(now() at time zone 'utc')"))
