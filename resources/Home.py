# -*- coding: utf-8 -*-

from flask_restful import Resource

class Home(Resource):
	def get(self):
		return {'info': 'Build with Flask-RESTful'}
