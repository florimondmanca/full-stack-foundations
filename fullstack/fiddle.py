from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# burger = session.query(MenuItem).filter_by(id=10).one()
# burger.price = '$2.99'
# session.add(burger)
# session.commit()
#
#
# for burger in session.query(MenuItem).filter_by(name='Veggie Burger'):
#     if burger.price != '$2.99':
#         burger.price = '$2.99'
#         session.add(burger)
# else:
#     session.commit()

# for burger in session.query(MenuItem).filter_by(name='Veggie Burger'):
#     print(burger.id)
#     print(burger.restaurant.name)
#     print(burger.price)
#     print()
