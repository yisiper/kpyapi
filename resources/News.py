# -*- coding: utf-8 -*-

from flask_restful import fields, marshal_with, reqparse, Resource, abort
from models.model import NewsTopicRepo

class CustomNewstopic(fields.Raw):
    def format(self, topics):
        topics = topics()
        topic_list = []
        for t in topics:
            topic_list.append(t.title)
        return topic_list

news_fields = {
    'id': fields.Integer,
    'title': fields.String,
    'slug': fields.String,
    'content': fields.String,
    'status': fields.String,
    'topics': CustomNewstopic(attribute='topic')
}

parser = reqparse.RequestParser()
parser.add_argument('title', type=str, required = True,
    help='No News title provided')
parser.add_argument('content', type=str, required = True,
    help='No News content provided')
parser.add_argument('topics', type=str, required = True,
    help='No News topics provided')

class News(Resource):
    def __init__(self):
        self.repo = NewsTopicRepo()

    @marshal_with(news_fields)
    def get(self, id=0):
        if (id) :
            try:
                lists = self.repo.get_news(id)
            except:
                abort(404)
        else :
            parser = reqparse.RequestParser()
            parser.add_argument('status', type=str, required = False)
            parser.add_argument('topic', type=str, required = False)
            args = parser.parse_args()

            if args.topic:
                topics = self.repo.in_topic(args.topic.split(','))
                if not topics:
                    abort(404, message="Unknown filter topic {} ".format(args.topic))

            lists = self.repo.list_news(args)
        return lists

    @marshal_with(news_fields)
    def post(self):
        args = parser.parse_args()
        self.in_topic(args)
        try:
            news = self.repo.add_news(args)
            return news, 201
        except:
           abort(409)

    def delete(self, id):
        try:
            self.repo.delete_news(id)
            return {}, 204
        except:
            abort(409)

    def put(self, id):
        args = parser.parse_args()
        self.in_topic(args)

        n = self.get(id)

        try:
            self.repo.edit_news(id, args)
            news = self.get(id)
            return news, 201
        except:
           abort(409)

    def in_topic(self, args):
        topics = [topics.strip() for topics in args.topics.split(',')]
        for t in topics:
            topic = self.repo.in_topic(t.split())
            if not topic:
                abort(404, message="Unknown topic {} ".format(t))


class NewsStatus(Resource):
    def __init__(self):
        self.repo = NewsTopicRepo()
        self.status = ['draft', 'publish'] #delete -> news

    def put(self, id):
        parser = reqparse.RequestParser()
        parser.add_argument('status', type=str, required = True,
            help='No Status provided')
        args = parser.parse_args()

        if args.status not in self.status:
            abort(404, message="Unknown news status {} ".format(args.status))
        
        News().get(id)

        try:
            self.repo.change_news_status(id, args.status)
            return News().get(id)
        except:
            abort(409)
