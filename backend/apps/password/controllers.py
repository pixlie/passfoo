from base.controllers import BaseController, ListMixin
from .models import Question
from .schema import QuestionSchema


class QuestionListController(BaseController, ListMixin):
    model = Question
    schema_class = QuestionSchema
