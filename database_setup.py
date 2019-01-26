#!/usr/bin/env python3
import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))

    @property
    def serialized(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'picture': self.picture
        }


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialized(self):

        return {
            'id': self.id,
            'name': self.name,
            'user_id': self.user_id
            }


class Item(Base):
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    title = Column(String(80), nullable=False)
    description = Column(String(250))
    cat_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    # We added this serialize function to be able to send JSON objects in a
# serializable format
    @property
    def serialized(self):

        return {

            'cat_id': self.cat_id,
            'description': self.description,
            'id': self.id,
            'title': self.title,
            'cat_name': self.category.name,
            'user_id': self.user_id
            }


engine = create_engine('sqlite:///catalog.db?check_same_thread=False')
Base.metadata.create_all(engine)
