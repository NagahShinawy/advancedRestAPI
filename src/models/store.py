from db import db
from typing import List, Dict, Union   # type hinting
from .item import item_json

store_json = Dict[str, Union[int, str, List[item_json]]]


class StoreModel(db.Model):
    __tablename__ = "stores"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)

    items = db.relationship("ItemModel", lazy="dynamic")

    def __init__(self, name: str):
        self.name = name

    def json(self) -> store_json:
        return {
            "id": self.id,
            "name": self.name,
            "items": [item.json() for item in self.items.all()],
        }

    @classmethod
    def find_by_name(cls, name: str) -> "StoreModel":   # return StoreModel obj
        return cls.query.filter_by(name=name).first()

    @classmethod
    def find_all(cls) -> List["StoreModel"]:   # return list of StoreModel objs
        return cls.query.all()

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()
