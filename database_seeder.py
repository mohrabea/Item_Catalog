#!/usr/bin/env python3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import User, Category, Item, Base

engine = create_engine('sqlite:///catalog.db?check_same_thread=False')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create dummy user
user1 = User(name="Mohammed Rabea",
             email="moh.rabea@gmail.com",
             picture='*')
session.add(user1)
session.commit()


# Item for Soccer
_category = Category(user=user1,
                     name="Soccer")

session.add(_category)
session.commit()

_item = Item(user=user1,
             title="Tow shinguards",
             description="tow shinguards **",
             category=_category)

session.add(_item)
session.commit()

_item = Item(user=user1, title="Shinguards",
             description="shinguards **",
             category=_category)

session.add(_item)
session.commit()

_item = Item(user=user1, title="Jersey",
             description="jersey **",
             category=_category)

session.add(_item)
session.commit()

_item = Item(user=user1, title="Soccr Cleats",
             description="soccr cleats **",
             category=_category)

session.add(_item)
session.commit()


# Item for Basketball
_category = Category(user=user1,
                     name="Basketball")

session.add(_category)
session.commit()

# Item for Baseball
_category = Category(user=user1,
                     name="Baseball")

_item = Item(user=user1,
             title="Bat",
             description="bat **",
             category=_category)

session.add(_item)
session.commit()


session.add(_category)
session.commit()

# Item for Frisbee
_category = Category(user=user1,
                     name="Frisbee")

session.add(_category)
session.commit()

# Item for Snowboarding
_category = Category(user=user1,
                     name="Snowboarding")

session.add(_category)
session.commit()

_item = Item(user=user1,
             title="Googles",
             description="googles **",
             category=_category)

session.add(_item)
session.commit()

_item = Item(user=user1,
             title="Snowboard",
             description="snowboard **",
             category=_category)

session.add(_item)
session.commit()

# Item for Rock Climbing
_category = Category(user=user1,
                     name="Rock Climbing")

session.add(_category)
session.commit()

# Item for Foosball
_category = Category(user=user1,
                     name="Foosball")

session.add(_category)
session.commit()

_item = Item(user=user1,
             title="Foosball",
             description="foosball **",
             category=_category)

session.add(_item)
session.commit()

# Item for Skating
_category = Category(user=user1,
                     name="Skating")

session.add(_category)
session.commit()

# Item for Hockey
_category = Category(user=user1,
                     name="Hockey")

session.add(_category)
session.commit()

_item = Item(user=user1,
             title="Stick",
             description="stick **",
             category=_category)

session.add(_item)
session.commit()


print("added category & items!")
