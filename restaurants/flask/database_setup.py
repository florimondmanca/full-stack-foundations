"""Database setup."""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy import Column, String, Integer, ForeignKey


Base = declarative_base()


class Restaurant(Base):
    __tablename__ = 'restaurant'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)

    @property
    def serialized(self):
        return {
            'name': self.name,
            'id': self.id,
        }


class MenuItem(Base):
    __tablename__ = 'menu_item'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    course = Column(String(250))
    description = Column(String(250))
    price = Column(String(8))
    restaurant_id = Column(Integer, ForeignKey('restaurant.id'))
    restaurant = relationship(Restaurant)

    @property
    def serialized(self):
        return {
            'name': self.name,
            'course': self.course,
            'description': self.description,
            'price': self.price,
            'id': self.id,
        }


engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.create_all(engine)
