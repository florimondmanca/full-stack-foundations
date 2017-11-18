"""Simple Flask project for restaurant menus."""

from flask import Flask, render_template, request, redirect, url_for, flash, \
    jsonify

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
def index():
    """Home page, with a list of all restaurants."""
    restaurants = db.query(Restaurant).all()
    return render_template('index.html', restaurants=restaurants)


# Restaurant CRUD

@app.route('/restaurants/<int:restaurant_id>/')
def restaurant_detail(restaurant_id):
    """Detail page of a restaurant."""
    restaurant = db.query(Restaurant).filter_by(id=restaurant_id).one()
    items = db.query(MenuItem).filter_by(restaurant=restaurant)
    return render_template('restaurant_detail.html', restaurant=restaurant, items=items)


@app.route('/restaurants/add/', methods=['GET', 'POST'])
def add_restaurant():
    """Add a new restaurant."""
    if request.method == 'POST':
        name = request.form['name']
        restaurant = Restaurant(name=name)
        db.add(restaurant)
        db.commit()
        flash(f'Successfully created restaurant {restaurant.name}.')
        return redirect(url_for('index'))
    return render_template('add_restaurant.html')


@app.route('/restaurants/<int:restaurant_id>/edit', methods=['GET', 'POST'])
def edit_restaurant(restaurant_id):
    """Edit a restaurant."""
    restaurant = db.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        name = request.form['name']
        restaurant.name = name
        db.add(restaurant)
        db.commit()
        flash(f'Successfully editted {restaurant.name}.')
        return redirect(url_for('restaurant_detail',
                                restaurant_id=restaurant_id))
    return render_template('edit_restaurant.html', restaurant=restaurant)


@app.route('/restaurants/<int:restaurant_id>/delete/', methods=['GET', 'POST'])
def delete_restaurant(restaurant_id):
    """Delete a restaurant."""
    restaurant = db.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        db.delete(restaurant)
        db.commit()
        flash(f'{restaurant.name} successfully deleted.')
        return redirect(url_for('index'))
    return render_template('delete_restaurant.html', restaurant=restaurant)


# MenuItem CRUD

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
        return redirect(url_for('restaurant_detail',
                                restaurant_id=restaurant_id))
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
        return redirect(url_for('restaurant_detail',
                                restaurant_id=restaurant_id))
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
        return redirect(url_for('restaurant_detail',
                                restaurant_id=restaurant_id))
    return render_template('delete_item.html',
                           restaurant=restaurant, item=item)


# API endpoints

@app.route('/api/restaurants/<int:restaurant_id>/')
def get_restaurant(restaurant_id):
    """API endpoint to get the menu of a restaurant."""
    restaurant = db.query(Restaurant).filter_by(id=restaurant_id).one()
    items = db.query(MenuItem).filter_by(restaurant=restaurant)
    return jsonify(name=restaurant.name,
                   items=[item.serialized for item in items])


@app.route('/api/restaurants/<int:restaurant_id>/items/<int:item_id>/')
def get_item(restaurant_id, item_id):
    """API endpoint to get an item from a restaurant's menu."""
    item = db.query(MenuItem).filter_by(id=item_id).one()
    return jsonify(item=item.serialized)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run()
