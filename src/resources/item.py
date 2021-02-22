from typing import Dict

from flask_restful import Resource, reqparse
from flask_jwt_extended import (
    jwt_required,
    fresh_jwt_required,
)
from models.item import ItemModel
from utils.errors import (
    BLANK_ERROR,
    OBJ_MOT_FOUND,
    NAME_ALREADY_EXISTS,
    ERROR_INSERTING,
    OBJ_DELETED
)
from utils import status


class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument(
        "price", type=float, required=True, help=BLANK_ERROR.format("price")
    )
    parser.add_argument(
        "store_id", type=int, required=True, help=BLANK_ERROR.format("store_id")
    )

    def get(self, name: str):
        item = ItemModel.find_by_name(name)
        if item:
            return item.json(), status.HTTP_200_OK
        return {"message": OBJ_MOT_FOUND.format(self.__class__.__name__)}, status.HTTP_404_NOT_FOUND

    @fresh_jwt_required
    def post(self, name: str):
        if ItemModel.find_by_name(name):
            return (
                {"message": NAME_ALREADY_EXISTS.format(obj=self.__class__.__name__, name=name)},
                status.HTTP_400_BAD_REQUEST,
            )

        data = Item.parser.parse_args()

        item = ItemModel(name, **data)

        try:
            item.save_to_db()
        except:
            return {"message": ERROR_INSERTING.format(self.__class__.__name__)}, status.HTTP_500_INTERNAL_SERVER_ERROR

        return item.json(), status.HTTP_201_CREATED

    @jwt_required
    def delete(self, name: str):
        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()
            return {"message": OBJ_DELETED.format(self.__class__.__name__)}, status.HTTP_200_OK
        return {"message": OBJ_MOT_FOUND.format(self.__class__.__name__)}, status.HTTP_404_NOT_FOUND

    def put(self, name: str):
        data = Item.parser.parse_args()

        item = ItemModel.find_by_name(name)

        if item:
            item.price = data["price"]
        else:
            item = ItemModel(name, **data)

        item.save_to_db()

        return item.json(), status.HTTP_200_OK


class ItemList(Resource):
    def get(self) -> Dict:
        return {"items": [item.json() for item in ItemModel.find_all()]}
