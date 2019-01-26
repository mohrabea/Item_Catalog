#!/usr/bin/env python3

from flask import Flask, render_template, request, url_for, redirect, flash, \
    jsonify
from flask import session as login_session
from sqlalchemy import create_engine, join
from sqlalchemy.orm import sessionmaker
from database_setup import User, Category, Item, Base
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
engine = create_engine('sqlite:///catalog.db?check_same_thread=False')

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Category"

DBSession = sessionmaker(bind=engine)
session = DBSession()


# |---------------------------------------------------|
# |               LOGIN TO GOOGLE+                    |
# |---------------------------------------------------|

# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already '
                                            'connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;' \
              '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print("done!")
    return output


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print('Access Token is None')
        response = make_response(json.dumps('Current user not connected.'),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # print('In gdisconnect access token is %s', access_token)
    # print('User name is: ')
    # print(login_session['username'])
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % \
          login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    # print('result is ')
    # print(result)
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        flash("Successfully Logout..")
        return redirect(url_for('home'))
    else:
        response = make_response(json.dumps('Failed to revoke token for given'
                                            ' user.'), 400)
        response.headers['Content-Type'] = 'application/json'
    return response


# |---------------------------------------------------|


# |---------------------------------------------------|
# |                  USER FUNCTION                    |
# |---------------------------------------------------|

# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
        'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except Exception:
        return None
        raise


# |---------------------------------------------------|


# |---------------------------------------------------|
# |                JSON ENDPOINT                      |
# |---------------------------------------------------|

# JSON ENDPOINT Hear to display all catalog
@app.route('/catalog.json')
def catalog_json():
    categories = []
    for c in session.query(Category).all():
        cat_output = {
            "id": c.id,
            "name": c.name
        }
        items = session.query(Item).filter_by(cat_id=c.id).all()
        if items:
            cat_output["item"] = [i.serialized for i in items]
        categories.append(cat_output)
    return jsonify(Category=categories)


# JSON ENDPOINT Here to display all categories
@app.route('/categories.json')
def categories_json():
    categories = session.query(Category).all()
    return jsonify(Category=[i.serialized for i in categories])


# JSON ENDPOINT Here to display all items
@app.route('/items.json')
def items_json():
    items = session.query(Item).order_by(Item.cat_id).all()
    return jsonify(Item=[i.serialized for i in items])


# JSON ENDPOINT Here to display all items
@app.route('/users.json')
def users_json():
    users = session.query(User).all()
    return jsonify(User=[i.serialized for i in users])


# |---------------------------------------------------|


# |---------------------------------------------------|
# |                    HOME                           |
# |---------------------------------------------------|
# app.route decorator hear to list all categories.
@app.route('/')
@app.route('/catalog')
def home():
    if 'username' not in login_session:
        isLoggedIn = False
        user_create = 0
    else:
        isLoggedIn = True
        user_create = login_session['user_id']

    print(isLoggedIn)
    categories = session.query(Category).all()
    items = session.query(Item).order_by(Item.id.desc()).limit(10)

    latest_Item = []
    for l in items:
        one_cat = session.query(Category).filter_by(id=l.cat_id).one()
        item_output = {
            'id': l.id,
            'title': l.title,
            'cat_id': l.cat_id,
            'cat_name': one_cat.name,
        }
        latest_Item.append(item_output)
    return render_template('home.html', categories=categories,
                           items=latest_Item, isLoggedIn=isLoggedIn,
                           user_create=user_create)


# Selecting a specific category shows you all the items available for that
# category.
@app.route('/catalog/<string:cat_name>/items/')
def category_items(cat_name):
    categories = session.query(Category).all()
    category = session.query(Category).filter_by(name=cat_name).one()
    items = session.query(Item).filter_by(cat_id=category.id). \
        order_by(Item.id.desc()).all()

    ary_items = []
    for l in items:
        item_output = {
            'id': l.id,
            'title': l.title,
            'cat_id': l.cat_id,
            'cat_name': cat_name,
        }
        ary_items.append(item_output)
    return render_template('listItemsCat.html', categories=categories,
                           cat_name=cat_name, items=ary_items)


# |---------------------------------------------------|


# |---------------------------------------------------|
# |               CATEGORY  FUNCTIONS                 |
# |---------------------------------------------------|

# app.route here To create new category
@app.route('/catalog/new', methods=['POST', 'GET'])
def category_new():
    if 'username' not in login_session:
        return redirect('/login')

    if request.method == 'POST':
        newItem = Category(name=request.form['name'],
                           user_id=login_session['user_id'])
        session.add(newItem)
        session.commit()
        flash("<New Category Successfully Created>")
        return redirect(url_for('home'))
    elif request.method == 'GET':
        return render_template('newCategory.html')


# app.route here To modify category.
@app.route('/catalog/<string:cat_name>/edit/', methods=['POST', 'GET'])
def category_edit(cat_name):
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        categoryToEdit = session.query(Category).filter_by(name=cat_name).one()
        categoryToEdit.name = request.form['name']
        session.add(categoryToEdit)
        session.commit()
        flash("Category <{0}> has been edited to <{1}>".
              format(cat_name, request.form['name']))
        return redirect(url_for('home'))
    else:
        return render_template('editCategory.html', cat_name=cat_name)


# app route here To delete category.
@app.route('/catalog/<string:cat_name>/delete/', methods=['POST', 'GET'])
def category_delete(cat_name):
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        categoryToDelete = session.query(Category).filter_by(name=cat_name). \
            one()
        itemsToDelete = session.query(Item).filter_by(
            cat_id=categoryToDelete.id).all()
        session.delete(categoryToDelete)
        session.commit()
        if itemsToDelete:
            for i in itemsToDelete:
                session.delete(i)
            session.commit()
        flash('%s Successfully Deleted' % categoryToDelete.name)
        return redirect(url_for('home'))
    else:
        return render_template('deleteCategory.html', cat_name=cat_name)


# |---------------------------------------------------|
# |                 ITEM FUNCTIONS                    |
# |---------------------------------------------------|
# route here to add new item
@app.route('/catalog/newItem', methods=['POST', 'GET'])
def item_new():
    if 'username' not in login_session:
        return redirect('/login')

    if request.method == 'POST':
        newItem = Item(title=request.form['title'],
                       description=request.form['description'],
                       cat_id=request.form['cat_id'],
                       user_id=login_session['user_id'])
        session.add(newItem)
        session.commit()
        flash("<New Item Successfully Created>")
        return redirect(url_for('home'))
    elif request.method == 'GET':
        categories = session.query(Category).filter_by(
            user_id=login_session['user_id']).order_by(Category.name).all()

        if len(categories) > 0:
            return render_template('newItem.html', categories=categories)
        else:
            return "<script> function myFunction() {alert('You do not have " \
                   "any category Under your authority. Please create new " \
                   "category Under your authority and then you can add " \
                   "items to it'); window.location.href = '/catalog';} " \
                   "</script><body onload='myFunction()'>"


# route to  shows specific item information.
@app.route('/catalog/<string:cat_name>/<string:item_title>/')
def item_information(cat_name, item_title):
    category = session.query(Category).filter_by(name=cat_name).one()
    item = session.query(Item).filter(Item.cat_id == category.id,
                                      Item.title == item_title).one()
    is_Creator = False
    if 'username' in login_session:
        if item.user_id == login_session['user_id']:
            is_Creator = True

    return render_template('itemInformation.html', cat_name=cat_name,
                           item_title=item_title,
                           item_description=item.description,
                           is_Creator=is_Creator)


# route here to edit item
@app.route('/catalog/<string:cat_name>/<string:item_title>/edit/',
           methods=['POST', 'GET'])
def item_edit(cat_name, item_title):
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        category = session.query(Category).filter_by(name=cat_name).one()
        item = session.query(Item).filter(Item.cat_id == category.id,
                                          Item.title == item_title).one()
        item.title = request.form['title']
        item.description = request.form['description']
        item.cat_id = request.form['cat_id']
        session.add(item)
        session.commit()
        flash("<Item Successfully Updated>")
        return redirect(url_for('category_items', cat_name=cat_name))
    elif request.method == 'GET':
        # This query collects the only category created by the authority user
        categories = session.query(Category).filter_by(
            user_id=login_session['user_id']).order_by(Category.name).all()
        category = session.query(Category).filter_by(name=cat_name).one()
        item = session.query(Item).filter(Item.cat_id == category.id,
                                          Item.title == item_title).one()
        return render_template('editItem.html', categories=categories,
                               item=item, cat_name=cat_name,
                               item_title=item_title)


# route here to delete item
@app.route('/catalog/<string:cat_name>/<string:item_title>/delete/',
           methods=['POST', 'GET'])
def item_delete(cat_name, item_title):
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        category = session.query(Category).filter_by(name=cat_name).one()
        item = session.query(Item).filter(Item.cat_id == category.id,
                                          Item.title == item_title).one()
        session.delete(item)
        session.commit()
        flash("<Item Successfully Deleted>")
        return redirect(url_for('category_items', cat_name=cat_name))
    elif request.method == 'GET':
        return render_template('deleteItem.html', cat_name=cat_name,
                               item_title=item_title)


# |---------------------------------------------------|


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
