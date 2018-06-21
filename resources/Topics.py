# -*- coding: utf-8 -*-

from flask_restful import fields, marshal_with, reqparse, Resource, abort, url_for
from models.model import NewsTopicRepo

class CustomNews(fields.Raw):
    def format(self, news):
        news = news()
        news_list = []
        for n in news:
            news_list.append({
                'id':n.id, 
                'title': n.title, 
                'slug': n.slug,
                })
        return news_list

topic_fields = {
    'id': fields.Integer,
    'title': fields.String,
    'slug': fields.String,
}

topic_news_fields = {
    'id': fields.Integer,
    'title': fields.String,
    'slug': fields.String,
    'news': CustomNews(attribute='news')
}


parser = reqparse.RequestParser()
parser.add_argument('title', type=str, required = True,
    help='No topic title provided')

class Topics(Resource):
    def __init__(self):
        self.repo = NewsTopicRepo()

    @marshal_with(topic_news_fields)
    def get(self, id=0):
        if (id) :
            try:
                lists = self.repo.get_topic(id)
            except:
                abort(404)
        else :
            lists = self.repo.list_topic()
        return lists

    @marshal_with(topic_fields)
    def post(self):
        args = parser.parse_args()
        try:
            new_topic = self.repo.add_topic(args)
            return new_topic, 201
        except:
           abort(409)

    def delete(self, id):
        try:
            self.repo.delete_topic(id)
            return {}, 204
        except:
            abort(409)