"""Simple webserver allowing to interact with the database."""

import re
from io import StringIO
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, HTTPServer
import cgi
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant


def create_db():
    """Create a database session and return it."""
    engine = create_engine('sqlite:///restaurantmenu.db')
    Base.metadata.bind = engine

    DBSession = sessionmaker(bind=engine)
    return DBSession()


db = create_db()


class WebServerHandler(BaseHTTPRequestHandler):
    """Simple webserver handler."""

    forms = {
        'hello': (
            "<form method='POST' enctype='multipart/form-data' "
            "action='/hello'>"
            "<h2>What would you like me to say?</h2>"
            "<input name='message' type='text'>"
            "<input type='submit' value='Submit'>"
            "</form>"
        ),
        'restaurant-add': (
            "<form method='POST' enctype='multipart/form-data'"
            "action='/restaurants/new'>"
            "<h1>Create a restaurant</h1>"
            "<input name='name' type='text'>"
            "<input type='submit' value='Create'>"
            "</form>"
        ),
        'restaurant-edit': (
            "<form method='POST' enctype='multipart/form-data'"
            "action='/restaurants/{id}/edit'>"
            "<h1>Edit a restaurant</h1>"
            "<h2>Enter a new name for {name}</h2>"
            "<input name='name' type='text'>"
            "<input type='submit' value='Edit'>"
            "</form>"
        ),
        'restaurant-delete': (
            "<form method='POST' action='/restaurants/{id}/delete'>"
            "<h1>Delete a restaurant</h1>"
            "<h2>Are you sure you want to delete {name}?</h2>"
            "<input type='submit' value='Confirm'>"
            "</form>"
            "<a href='/restaurants'>Back</a>"
        ),
    }
    regex = {
        'restaurant-edit': r'/restaurants/(?P<id>\d+)/edit$',
        'restaurant-delete': r'/restaurants/(?P<id>\d+)/delete$',
    }

    @contextmanager
    def page(self):
        """Context manager.

        Ensures the page starts and ends with HTML and body tags.
        Return a string stream.
        """
        page = StringIO()
        page.write("<html><body>")
        yield page
        page.write("</body></html>")
        output = page.getvalue()
        self.writebytes(output)

    # helper methods

    def default_header(self, status_code, redirect=None):
        self.send_response(status_code)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        if redirect:
            self.send_header('Location', redirect)
        self.end_headers()

    def writebytes(self, s):
        self.wfile.write(bytes(s, 'utf-8'))

    # request handlers

    def do_GET(self):
        try:
            # list restaurant page
            if self.path.endswith('/restaurants'):
                self.default_header(200)
                restaurants = db.query(Restaurant).all()
                with self.page() as page:
                    for restaurant in restaurants:
                        page.write('<p>')
                        page.write(restaurant.name)
                        edit_url = f'/restaurants/{restaurant.id}/edit'
                        page.write(f"<br/><a href='{edit_url}'>Edit</a>")
                        delete_url = f'/restaurants/{restaurant.id}/delete'
                        page.write(f"<br/><a href='{delete_url}'>Delete</a>")
                        page.write('</p>')
                    page.write('<a href="/restaurants/new">Add restaurant</a>')

            # add restaurant page
            if self.path.endswith('/restaurants/new'):
                self.default_header(200)
                with self.page() as page:
                    page.write(self.forms['restaurant-add'])

            # edit restaurant page
            regex = self.regex['restaurant-edit']
            m = re.search(regex, self.path)
            if m:
                self.default_header(200)
                id_ = m.group('id')
                restaurant = db.query(Restaurant).get(id_)
                if restaurant is None:
                    raise IOError
                with self.page() as page:
                    page.write(self.forms['restaurant-edit'].format(
                        id=id_,
                        name=restaurant.name))

            # delete restaurant page
            regex = self.regex['restaurant-delete']
            m = re.search(regex, self.path)
            if m:
                self.default_header(200)
                id_ = m.group('id')
                restaurant = db.query(Restaurant).get(id_)
                if restaurant is None:
                    raise IOError
                with self.page() as page:
                    page.write(self.forms['restaurant-delete'].format(
                        id=id_,
                        name=restaurant.name))

            if self.path.endswith('/hello'):
                self.default_header(200)
                with self.page() as page:
                    page.write('Hello!')
                    page.write(self.forms['hello'])

        except IOError as e:
            self.send_error(404, f'File not found: {self.path}')

    def do_POST(self):
        try:
            # add restaurant
            if self.path.endswith('/restaurants/new'):
                ctype, pdict = cgi.parse_header(self.headers['content-type'])
                pdict['boundary'] = pdict['boundary'].encode()
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    name_content = fields.get('name')
                name = name_content[0].decode()

                restaurant = Restaurant(name=name)
                db.add(restaurant)
                db.commit()

                self.default_header(301, redirect='/restaurants')

            # edit restaurant
            regex = self.regex['restaurant-edit']
            m = re.search(regex, self.path)
            if m:
                id_ = m.group('id')
                ctype, pdict = cgi.parse_header(self.headers['content-type'])
                pdict['boundary'] = pdict['boundary'].encode()
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    name_content = fields.get('name')
                name = name_content[0].decode()

                restaurant = db.query(Restaurant).get(id_)
                if restaurant is None:
                    raise IOError

                restaurant.name = name
                db.add(restaurant)
                db.commit()

                self.default_header(301, redirect='/restaurants')

            # delete restaurant
            regex = self.regex['restaurant-delete']
            m = re.search(regex, self.path)
            if m:
                id_ = m.group('id')

                restaurant = db.query(Restaurant).get(id_)
                if restaurant is None:
                    raise IOError

                db.delete(restaurant)
                db.commit()

                self.default_header(301, redirect='/restaurants')

            elif self.path.endswith('/hello'):
                self.default_header(301)

                ctype, pdict = cgi.parse_header(self.headers['content-type'])
                pdict['boundary'] = pdict['boundary'].encode()
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('message')
                message = messagecontent[0].decode()

                with self.page() as page:
                    page.write(
                        "<h2>Okay, how about this?</h2>"
                        f"<h1>{message}</h1>"
                    )
                    page.write(self.forms['hello'])

        except Exception as e:
            raise


def main():
    """Main webserver loop."""
    try:
        port = 8080
        server = HTTPServer(('', port), WebServerHandler)
        print(f'Server running on port {port}.')
        server.serve_forever()
    except KeyboardInterrupt:
        print('Stopping the server...')
        server.socket.close()


if __name__ == '__main__':
    main()
