# -*- coding: utf-8 -*-

from tellduslive.base import LiveMessage
import logging
import time

class Condition(object):
	def __init__(self, event, id, group, **kwargs):
		super(Condition,self).__init__()
		self.event = event
		self.id = id
		self.group = group

	def loadParams(self, params):
		for param in params:
			try:
				self.parseParam(param, params[param])
			except Exception as e:
				logging.error(str(e))
				logging.error("Could not parse condition param, %s - %s" % (param, params[param]))

	def parseParam(self, name, value):
		pass

	def validate(self, success, failure):
		failure()

class RemoteCondition(Condition):
	def __init__(self, **kwargs):
		super(RemoteCondition,self).__init__(**kwargs)
		self.outstandingRequests = []

	def receivedResultFromServer(self, result):
		for request in self.outstandingRequests:
			age = time.time() - request['started']
			if age > 30:
				# Too old
				continue
			if result == 'success':
				request['success']()
			else:
				request['failure']()
		self.outstandingRequests = []

	def validate(self, success, failure):
		self.outstandingRequests.append({
			'started': time.time(),
			'success': success,
			'failure': failure,
		})
		msg = LiveMessage('event-validatecondition')
		msg.append({
			'condition': self.id
		})
		self.event.manager.live.send(msg)
