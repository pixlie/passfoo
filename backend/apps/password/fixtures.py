from .models import Question, QuestionDataType


def generate():
    Question(
        text="Your date of birth",
        password_text="What is your date of birth?",
        data_type=QuestionDataType.STRING,
        related_id=None
    ).save()

    Question(
        text="Place of birth",
        password_text="What is your place of birth?",
        data_type=QuestionDataType.STRING,
        related_id=None
    ).save()

    Question(
        text="Your secret superhero",
        password_text="Name of your secret superhero?",
        data_type=QuestionDataType.STRING,
        related_id=None
    ).save()

    q = Question(
        text="If you are/had been married",
        password_text="Marital details",
        data_type=QuestionDataType.CATEGORY,
        related_id=None
    )
    q.save()

    Question(
        text="Name of your spose",
        password_text="First name of your spouse?",
        data_type=QuestionDataType.STRING,
        related_id=q.id
    ).save()

    Question(
        text="Date of marriage",
        password_text="Date of your marriage?",
        data_type=QuestionDataType.DATE,
        related_id=q.id
    ).save()

    Question(
        text="Place of marriage",
        password_text="Where did you get married?",
        data_type=QuestionDataType.STRING,
        related_id=q.id
    ).save()

    Question(
        text="Secret superpower",
        password_text="What is your secret superpower?",
        data_type=QuestionDataType.STRING,
        related_id=None
    ).save()

    Question(
        text="Favorite villain/hero",
        password_text="Who is your favorite villain/hero?",
        data_type=QuestionDataType.STRING,
        related_id=None
    ).save()
