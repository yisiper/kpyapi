
from peewee import *
from slugify import slugify
import datetime

db = SqliteDatabase('news_topic.db')
qlimit = 10

class BaseModel(Model):
    class Meta:
        database = db

class News(BaseModel):
   id=AutoField()
   title=CharField()
   slug=CharField(unique=True)
   content=TextField()
   status=CharField()
   created_at=DateTimeField()
   updated_at=DateTimeField(null = True)

   def topic(self):
        return list(Topic
            .select()
            .join(NewsTopic, on=NewsTopic.topic_id)
            .where(NewsTopic.news_id == self)
            .order_by(Topic.created_at.desc()))

class Topic(BaseModel):
   id=AutoField()
   title=CharField()
   slug=CharField(unique=True)
   created_at=DateTimeField()
   updated_at=DateTimeField(null=True)

   def news(self):
        return list(News
            .select()
            .join(NewsTopic, on=NewsTopic.news_id)
            .where(NewsTopic.topic_id == self)
            .order_by(News.created_at.desc()).limit(qlimit))

class NewsTopic(BaseModel):
   id=AutoField()
   news_id=ForeignKeyField(News, backref='news')
   topic_id=ForeignKeyField(Topic, backref='topic')
   created_at=DateTimeField()
   deleted_at=DateTimeField(null=True)


# simple utility function to create tables
class ModelTable:
    def create_tables():
        with db:
            db.create_tables([News, Topic, NewsTopic])
    def drop_tables():
        with db:
            db.drop_tables([News, Topic, NewsTopic])

class NewsTopicRepo:
    def add_topic(self, args):
        return Topic.create(
            title= args['title'],
            slug= slugify(args['title']),
            created_at= datetime.datetime.now()
            )
    def get_topic(self, id):
        return Topic.get(Topic.id == id)

    def list_topic(self):
        return list(Topic.select().limit(qlimit))

    def delete_topic(self, id):
        return Topic.delete().where(Topic.id == id).execute()

    def in_topic(self, args):
        return list(Topic.select().where(Topic.title << args))

    def add_news(self, args):
        with db.atomic():
            news = News.create(
                title = args['title'],
                slug = slugify(args['title']),
                content = args['content'],
                status = 'draft',
                created_at = datetime.datetime.now()
                )

            topics = self.in_topic(args['topics'].split(','))
            for topic in topics:
                NewsTopic.create(
                    news_id = news.id, 
                    topic_id = topic.id, 
                    created_at=datetime.datetime.now())
            
        return news
    def get_news(self, id):
        return News.get(News.id == id, News.status != 'deleted')

    def list_news(self, args):
        query = News.select()
        if 'status' in args:
            if args.status:
                query = query.where(News.status == args.status)

        if 'topic' in args:
            if args.topic:
                topics = self.in_topic(args.topic.split(','))
                topic = topics[0]
                query = query.join(NewsTopic, on= NewsTopic.news_id).where(NewsTopic.topic_id == topic.id)

        query = query.limit(qlimit)
        return list(query)

    def edit_news(self, id, args):
        with db.atomic():
            news = self.get_news(id)
            u = {
                'title' : args.title,
                'content' : args.content,
                'updated_at' : datetime.datetime.now(),
            }

            if args.title != news.title:
                u['slug'] = slugify(args.title)

            new_one = News.update(
                **u
            ).where(News.id == news.id).execute()

            NewsTopic.delete().where(NewsTopic.news_id == id).execute()

            topics = self.in_topic(args['topics'].split(','))
            for topic in topics:
                NewsTopic.create(
                    news_id = news.id, 
                    topic_id = topic.id, 
                    created_at=datetime.datetime.now())
        return new_one

    def delete_news(self, id):
        return News.update(status='deleted').where(News.id == id).execute()

    def change_news_status(self, id, to_status):
        with db.atomic():
            st = News.update(status = to_status).where(News.id == id).execute()
        return st