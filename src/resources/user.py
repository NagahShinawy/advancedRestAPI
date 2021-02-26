from flask_restful import Resource, reqparse
from werkzeug.security import safe_str_cmp
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_refresh_token_required,
    get_jwt_identity,
    jwt_required,
    get_raw_jwt,
)
import datetime
from models.user import UserModel
from blacklist import BLACKLIST
from utils import status
from utils.errors import (
    BLANK_ERROR,
    OBJ_MOT_FOUND,
    NAME_ALREADY_EXISTS,
    INVALID_USERNAME_OR_PASSWORD,
)
from utils.success import CREATED_SUCCESSFULLY, LOGOUT_SUCCESSFULLY

_user_parser = reqparse.RequestParser()
_user_parser.add_argument(
    "username", type=str, required=True, help=BLANK_ERROR.format("username")
)
_user_parser.add_argument(
    "password", type=str, required=True, help=BLANK_ERROR.format("password")
)


class UserRegister(Resource):
    def post(self):
        data = _user_parser.parse_args()

        if UserModel.find_by_username(data["username"]):
            return {
                "message": NAME_ALREADY_EXISTS.format(
                    cls=self.__class__.__name__, name=data["username"]
                )
            }, status.HTTP_400_BAD_REQUEST

        user = UserModel(**data)
        user.save_to_db()

        return {"message": CREATED_SUCCESSFULLY}, status.HTTP_201_CREATED


class User(Resource):
    """
    This resource can be useful when testing our Flask app. We may not want to expose it to public users, but for the
    sake of demonstration in this course, it can be useful when we are manipulating data regarding the users.
    """

    @classmethod
    def get(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {
                "message": OBJ_MOT_FOUND.format(cls=cls.__name__)
            }, status.HTTP_404_NOT_FOUND
        return user.json(), status.HTTP_200_OK

    @classmethod
    def delete(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {
                "message": OBJ_MOT_FOUND.format(cls=cls.__name__)
            }, status.HTTP_404_NOT_FOUND
        user.delete_from_db()
        return "", status.HTTP_204_NO_CONTENT


class UserLogin(Resource):
    def post(self):
        data = _user_parser.parse_args()

        user = UserModel.find_by_username(data["username"])

        # this is what the `authenticate()` function did in security.py
        if user and safe_str_cmp(user.password, data["password"]):
            # identity= is what the identity() function did in security.py—now stored in the JWT
            access_token = create_access_token(
                identity=user.id,
                fresh=True,
                expires_delta=datetime.timedelta(minutes=15),
            )
            refresh_token = create_refresh_token(user.id)
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
            }, status.HTTP_200_OK

        return {"message": INVALID_USERNAME_OR_PASSWORD}, status.HTTP_401_UNAUTHORIZED


class UserLogout(Resource):
    @jwt_required
    def post(self):
        jti = get_raw_jwt()["jti"]  # jti is "JWT ID", a unique identifier for a JWT.
        user_id = get_jwt_identity()
        BLACKLIST.add(jti)
        return {"message": LOGOUT_SUCCESSFULLY.format(id=user_id)}, status.HTTP_200_OK


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token": new_token}, status.HTTP_200_OK
