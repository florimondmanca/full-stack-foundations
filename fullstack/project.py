"""Simple Flask project for restaurant menus."""

from random import randint
from flask import Flask, render_template, request, redirect, url_for, flash

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem


def create_db():
    """Create a database session and return it."""
    engine = create_engine('sqlite:///restaurantmenu.db')
    Base.metadata.bind = engine

    DBSession = sessionmaker(bind=engine)
    return DBSession()


app = Flask(__name__)
db = create_db()


@app.route('/')
def show_random_restaurant_menu():
    query = db.query(Restaurant)
    if query.count():
        index = randint(0, query.count() - 1)
        restaurant = query.all()[index]
        return redirect(url_for('show_menu', restaurant_id=restaurant.id))
    else:
        return 'No restaurants!'


@app.route('/restaurants/<int:restaurant_id>/items')
def show_menu(restaurant_id):
    """List the items of a restaurant."""
    restaurant = db.query(Restaurant).filter_by(id=restaurant_id).one()
    items = db.query(MenuItem).filter_by(restaurant=restaurant)
    return render_template('menu.html', restaurant=restaurant, items=items)


@app.route('/restaurants/<int:restaurant_id>/items/add/',
           methods=['GET', 'POST'])
def add_item(restaurant_id):
    """Add an item to a restaurant's menu."""
    restaurant = db.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        name = request.form['name']
        item = MenuItem(name=name, restaurant=restaurant)
        db.add(item)
        db.commit()
        flash(f'Successfully added {item.name}.')
        return redirect(url_for('show_menu', restaurant_id=restaurant_id))
    return render_template('add_item.html', restaurant=restaurant)


@app.route('/restaurants/<int:restaurant_id>/items/<int:item_id>/edit/',
           methods=['GET', 'POST'])
def edit_item(restaurant_id, item_id):
    """Edit an item of a restaurant's menu."""
    restaurant = db.query(Restaurant).filter_by(id=restaurant_id).one()
    item = db.query(MenuItem).filter_by(id=item_id).one()
    if request.method == 'POST':
        item.name = request.form['name']
        db.add(item)
        db.commit()
        flash(f'{item.name} successfully edited.')
        return redirect(url_for('show_menu', restaurant_id=restaurant_id))
    return render_template('edit_item.html', restaurant=restaurant, item=item)


@app.route('/restaurants/<int:restaurant_id>/items/<int:item_id>/delete/',
           methods=['GET', 'POST'])
def delete_item(restaurant_id, item_id):
    """Delete an item from a restaurant's menu."""
    restaurant = db.query(Restaurant).filter_by(id=restaurant_id).one()
    item = db.query(MenuItem).filter_by(id=item_id).one()
    if request.method == 'POST':
        db.delete(item)
        db.commit()
        flash(f'{item.name} successfully deleted.')
        return redirect(url_for('show_menu', restaurant_id=restaurant_id))
    return render_template('delete_item.html',
                           restaurant=restaurant, item=item)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run()
