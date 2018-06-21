# -*- coding: utf-8 -*-
import unittest
from api import app
from models.model import ModelTable

class TestTopic(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
    def setUpClass():
        ModelTable.create_tables()

    def test_list_topics(self):
        resp = self.client.get('/topic')
        self.assertEqual(resp.status_code, 200)

    def test_create_and_get_and_delete_topic(self):
        t = {
            'title' : 'pialaduniarusia'
        };
        with self.client as c:
            resp = c.post('/topic', json= t)
            topic = resp.get_json()
            self.assertEqual(resp.status_code, 201)
            self.assertEqual(t['title'], topic['title'])

            resp = c.get('topic/%d' %topic['id'])
            get = resp.get_json()
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(get['id'], topic['id'])

            resp = c.delete('topic/%d' %topic['id'])
            self.assertEqual(resp.status_code, 204)

    def test_get_topic_notfound(self):
        resp = self.client.get('topic/topic_not_found')
        self.assertEqual(resp.status_code, 404)

class TestNews(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.n = {
            'title' : 'CR Hat Trick',
            'content': 'CR do hat trick',
            'topics': 'pialadunia2018,portugal2018'
        }
    def setUpClass():
        ModelTable.create_tables()

    def tearDownClass():
        ModelTable.drop_tables()

    def test_list_news(self):
        with app.test_client() as c:
            resp = c.get('/news')
            self.assertEqual(resp.status_code, 200)

    def test_create_and_get_news(self):
        n = self.n
        with self.client as c:
            resp = c.post('/topic', json= {'title' : 'pialadunia2018'})
            resp = c.post('/topic', json= {'title' : 'portugal2018'})

            resp = c.post('/news', json= n)
            new = resp.get_json()
            self.assertEqual(resp.status_code, 201)
            self.assertEqual(n['title'], new['title'])

            resp = c.get('news/%d' %new['id'])
            get = resp.get_json()
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(get['id'], new['id'])

    def test_create_change_publish(self):
        status = 'publish'
        n = self.get_latest_news()
        resp = self.client.put('/news/%d/status' %n['id'], json= { 'status' : status})
        self.assertEqual(resp.status_code, 200)

        r = resp.get_json()
        self.assertEqual(r['status'], status)        

    def test_create_change_draft(self):
        status = 'draft'
        n = self.get_latest_news()
        resp = self.client.put('/news/%d/status' %n['id'], json= { 'status' : status})
        self.assertEqual(resp.status_code, 200)

        r = resp.get_json()
        self.assertEqual(r['status'], status)        

    def test_create_filter_news(self):
        with app.test_client() as c:
            resp = c.get('/news?status=draft&topic=pialadunia2018')
            self.assertEqual(resp.status_code, 200)

            resp = c.get('/news?status=xxx_non_exists&topic=xxx_non_exists')
            self.assertEqual(resp.status_code, 404)

    def test_delete_news(self):
        n = self.get_latest_news()
        resp = self.client.delete('news/%d' %n['id'])
        self.assertEqual(resp.status_code, 204)

    def get_latest_news(self):
        with app.test_client() as c:
            resp = c.get('/news')
            self.assertEqual(resp.status_code, 200)

        return  resp.get_json()[0]

if __name__ == '__main__':
    unittest.main()