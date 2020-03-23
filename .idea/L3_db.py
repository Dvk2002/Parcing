
import L3_data
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (Column,Integer,ForeignKey,String,)
from pymongo import MongoClient
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
Column,
Integer,
ForeignKey,
String,

)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.orm.session import Session



Base = declarative_base()



class Post(Base):
    __tablename__ = 'post'
    id = Column(Integer, primary_key = True, autoincrement= True)
    title_name = Column(String, nullable= True)
    url = Column(String, nullable= True)
    comment_counts = Column(String)
    date_time = Column(String)
    comment = relationship('Comments', back_populates='post')


    def __init__(self, title_name, url, date_time,comment_counts):
        self.title_name = title_name
        self.comment_counts = comment_counts
        self.url = url
        self.date_time = date_time



class Authors(Base):
    __tablename__ = 'authors'
    id = Column(Integer, primary_key = True, autoincrement= True)
    author_name = Column(String, nullable= True)
    author_url = Column(String, nullable= True, unique= True)
    comment = relationship('Comments', back_populates='author')

    def __init__(self, author_name, author_url):
        self.author_name = author_name
        self.author_url = author_url



class AuthorsComments(Base):
    __tablename__ = 'authors_comments'
    id = Column(Integer, primary_key=True, autoincrement=True)
    author_comments_name = Column(String, nullable=True)
    author_comments_url = Column(String, nullable=True, unique=True)
    comment = relationship('Comments', back_populates='author_comment')


    def __init__(self, author_comments_name, author_comments_url):
        self.author_comments_name = author_comments_name
        self.author_comments_url = author_comments_url

class Comments(Base):
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True, autoincrement=True)
    comment = Column(String, nullable=True, default='comment')
    author_id = Column(Integer, ForeignKey('authors.id'))
    author = relationship('Authors', back_populates='comment')
    author_comment_id = Column(Integer, ForeignKey('authors_comments.id'))
    author_comment = relationship('AuthorsComments', back_populates='comment')
    post_id = Column(Integer, ForeignKey('post.id'))
    post = relationship('Post', back_populates='comment')

    def __init__(self, post_id, author_comments_id, author_id, post):
        self.post_id = post_id
        self.author_comments_id = author_comments_id
        self.author_id = author_id
        self.post = post

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.orm.session import Session


engine = create_engine('sqlite:///hubr_new.db')
Base.metadata.create_all(engine)
session_db = sessionmaker(bind = engine)
session = session_db()


for pages in L3_data.get_pages(L3_data.soup):
    L3_data.get_posts(L3_data.soup)
# print(L3_data.data)

client = MongoClient('mongodb://localhost:27017/')

db = client['hubr_new']

# db['posts'].insert_many(data)

for key, value in L3_data.data.items():
    # print(key, value)
    db['posts'].insert_one({key: value})


for nick, url in L3_data.authors_comments_data.items():
    authors_comments = AuthorsComments(nick, url)
    session.add(authors_comments)
    try:
        session.commit()
    except Exception as e:
        session.rollback()

for nick, url in L3_data.authors_data.items():
    authors = Authors(nick, url)
    session.add(authors)
    try:
        session.commit()
    except Exception as e:
        session.rollback()


for title_name in L3_data.data.keys():

    post = Post(title_name, L3_data.data[title_name]['url'], L3_data.data[title_name]['comments_counts'], L3_data.data[title_name]['date_time'])

    session.add(post)
    session.add(authors)

    try:
        session.commit()
    except Exception as e:
        session.rollback()

session.close()