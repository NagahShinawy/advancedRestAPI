from marshmallow import Schema, fields, validates, ValidationError, INCLUDE, EXCLUDE


class BookSchema(Schema):
    title = fields.String(required=True)
    author = fields.String(required=True)
    description = fields.String(required=False)

    @validates("title")
    def validate_title(self, value):
        if len(value) > 50:
            raise ValidationError(f"'{value}' is more than 5 chars ")
        return value

    @validates("author")
    def validate_author(self, value):
        if len(value) > 50:
            raise ValidationError(f"'{value}' is more than 5 chars ")
        return value

    #
    # @validates("description")
    # def validate_description(self, value):
    #     if len(value) > 10:
    #         raise ValidationError(f"description is more than 300 chars")
    #     return value


class Book:
    def __init__(self, title, author, description):
        self.title = title
        self.author = author
        self.description = description

    def __repr__(self):
        return f"<{self.title}>"


if __name__ == "__main__":
    clean_code = Book("Clean Code", "Bob", "Book to write clean code")
    flask_api = Book("Flask for Building API", "martin", "Build API with flask")
    # print(clean_code)
    # print(flask_api)

    book_schema = BookSchema()  # 1- create Schema
    clean_code_serialization = book_schema.dump(
        clean_code
    )  # 2- dump book obj to be serialization (dictionary)
    flask_api_serialization = book_schema.dump(
        flask_api
    )  # 3- dump book obj to be serialization  (dictionary)
    print(clean_code_serialization)
    print(flask_api_serialization)
    print("#" * 50)
    body = {
        "title": "Django for building API",
        "author": "Nagah Shaban Shinawy",
        "description": "Learn to Build API with django & rest",
    }
    # if "description" at dictionary but not at Schema, but we need to deserialize it .
    # we can do that with unknown=INCLUDE to avoid error of "validationError: {'description': ['Unknown field.']}"
    #  اعمل INCLUDE للفيلد ال unknown وبالتالى هيظهر فى ال dictionary
    #  اعمل EXCLUDE للفيلد ال unknown وبالتالى مش هيظهر فى ال dictionary
    django_book = book_schema.load(
        body, unknown=EXCLUDE
    )  # from dictionary to book obj (deserialization)
    print(django_book)  # still dictionary but
    book = Book(**django_book)
    print(book)
