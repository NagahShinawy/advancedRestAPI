from flask_restful import Resource
from models.store import StoreModel
from utils.errors import (
    OBJ_MOT_FOUND,
    NAME_ALREADY_EXISTS,
    ERROR_INSERTING,
    get_class_name,
)
from utils import status


class Store(Resource):
    def get(self, name: str):
        store = StoreModel.find_by_name(name)
        if store:
            return store.json()
        return {
            "message": OBJ_MOT_FOUND.format(cls=get_class_name(self))
        }, status.HTTP_404_NOT_FOUND

    def post(self, name: str):
        if StoreModel.find_by_name(name):
            return (
                {
                    "message": NAME_ALREADY_EXISTS.format(
                        cls=get_class_name(self), name=name
                    )
                },
                status.HTTP_400_BAD_REQUEST,
            )

        store = StoreModel(name)
        try:
            store.save_to_db()
        except:
            return {
                "message": ERROR_INSERTING.format(get_class_name(self))
            }, status.HTTP_500_INTERNAL_SERVER_ERROR

        return store.json(), status.HTTP_201_CREATED

    def delete(self, name: str):
        store = StoreModel.find_by_name(name)
        if store:
            store.delete_from_db()
            # return {"message": "Store deleted."}, 204
            return "", status.HTTP_204_NO_CONTENT
        return {
            "message": OBJ_MOT_FOUND.format(cls=get_class_name(self))
        }, status.HTTP_404_NOT_FOUND


class StoreList(Resource):
    def get(self: str):
        return {"stores": [x.json() for x in StoreModel.find_all()]}
