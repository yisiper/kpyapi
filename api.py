# -*- coding: utf-8 -*-

from flask import Flask
from flask_restful import Api
from resources.News import News
from resources.Home import Home
from resources.News import NewsStatus
from resources.Topics import Topics
from models.model import ModelTable

app = Flask(__name__)
api = Api(app)

api.add_resource(Home, '/')
api.add_resource(News, '/news', '/news/<int:id>', endpoint='news')
api.add_resource(NewsStatus, '/news', '/news/<int:id>/status')
api.add_resource(Topics, '/topic', '/topic/<int:id>', endpoint='topic')

if __name__ == '__main__':
	ModelTable.create_tables()
	app.run()
