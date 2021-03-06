# -*- coding: utf-8 -*-

import httplib, logging, time
import netifaces
import xml.parsers.expat
from board import Board

class ServerList():

	def __init__(self):
		self.list = []
		self.listAge = 0

	def popServer(self):
		if (time.time() - self.listAge) > 1800:  # 30 minutes
			self.list = []
		if (self.list == []):
			try:
				self.retrieveServerList()
			except Exception as e:
				logging.error("Could not retrieve server list: %s", str(e))
				return False

		if (self.list == []):
			return False

		return self.list.pop(0)

	def retrieveServerList(self):
		conn = httplib.HTTPConnection('%s:80' % Board.liveServer())
		conn.request('GET', "/server/assign?protocolVersion=2&mac=%s" % ServerList.getMacAddr(Board.networkInterface()))
		response = conn.getresponse()

		p = xml.parsers.expat.ParserCreate()

		p.StartElementHandler = self._startElement
		p.Parse(response.read())
		self.listAge = time.time()

	def _startElement(self, name, attrs):
		if (name == 'server'):
			self.list.append(attrs)

	@staticmethod
	def getMacAddr(ifname):
		addrs = netifaces.ifaddresses(ifname)[netifaces.AF_LINK]
		try:
			mac = addrs[netifaces.AF_LINK][0]['addr']
		except IndexError, KeyError:
			return ''
		return mac.upper().replace(':', '')
