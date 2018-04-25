from .controllers import QuestionListController


def add_routes(app):
    app.add_route(QuestionListController.as_view(), "/q")
