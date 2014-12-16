# -*- coding: utf-8 -*-

from base import Application, Plugin
from telldus import DeviceManager, Device
from Protocol import Protocol
from Adapter import Adapter
from RF433Msg import RF433Msg
import logging

class RF433Node(Device):
	def __init__(self):
		super(RF433Node,self).__init__()
		self._nodeId = 0

	def localId(self):
		return self._nodeId

	def setId(self, newId):
		self._nodeId = newId
		super(RF433Node,self).setId(newId)

	def setNodeId(self, nodeId):
		self._nodeId = nodeId

	def typeString(self):
		return '433'

class SensorNode(RF433Node):
	def __init__(self):
		super(SensorNode,self).__init__()
		self._protocol = ''
		self._model = ''
		self._sensorId = 0

	def compare(self, protocol, model, sensorId):
		if self._protocol != protocol:
			return False
		if self._model != model:
			return False
		if self._sensorId != sensorId:
			return False
		return True

	def isDevice(self):
		return False

	def isSensor(self):
		return True

	def params(self):
		return {
			'protocol': self._protocol,
			'model': self._model,
			'sensorId': self._sensorId,
			'type': 'sensor',
		}

	def setParams(self, params):
		self._protocol = params.setdefault('protocol', '')
		self._model = params.setdefault('model', '')
		self._sensorId = params.setdefault('sensorId', 0)

	def updateValues(self, data):
		for value in data:
			self.setSensorValue(value['type'], value['value'], value['scale'])

class DeviceNode(RF433Node):
	def __init__(self, controller):
		super(DeviceNode,self).__init__()
		self.controller = controller

	def command(self, action, value=None, origin=None, success=None, failure=None, callbackArgs=[]):
		pass  # TODO

	def isDevice(self):
		return True

	def isSensor(self):
		return False

	def methods(self):
		return 3

	def params(self):
		return {
			'type': 'device',
		}

	def setParams(self, params):
		pass

class RF433(Plugin):
	def __init__(self):
		self.version = 0
		self.devices = []
		self.sensors = []
		self.dev = Adapter(self, '/dev/ttyUSB1')
		deviceNode = DeviceNode(self.dev)
		self.deviceManager = DeviceManager(self.context)
		for d in self.deviceManager.retrieveDevices('433'):
			p = d.params()
			if 'type' not in p:
				continue
			if p['type'] == 'sensor':
				device = SensorNode()
				self.sensors.append(device)
			else:
				continue
			device.setNodeId(d.id())
			device.setParams(p)
			self.deviceManager.addDevice(device)

		self.deviceManager.finishedLoading('433')
		self.dev.queue(RF433Msg('V', success=self.__version, failure=self.__noVersion))

	def decode(self, msg):
		if 'class' in msg and msg['class'] == 'sensor':
			self.decodeSensor(msg)
			return

	def decodeData(self, cmd, params):
		if cmd == 'W':
			self.decode(params)
		elif cmd == 'V':
			# New version received, probably after firmware upload
			self.__version(params)
		else:
			logging.debug("Unknown data: %s", str(cmd))

	def decodeSensor(self, msg):
		protocol = Protocol.protocolInstance(msg['protocol'])
		if not protocol:
			logging.error("No known protocol for %s", msg['protocol'])
			return
		data = protocol.decodeData(msg)
		if not data:
			return
		p = data['protocol']
		m = data['model']
		sensorId = data['id']
		sensorData = data['values']
		sensor = None
		for s in self.sensors:
			if s.compare(p, m, sensorId):
				sensor = s
				break
		if sensor is None:
			sensor = SensorNode()
			sensor.setParams({'protocol': p, 'model': m, 'sensorId': sensorId})
			self.sensors.append(sensor)
			self.deviceManager.addDevice(sensor)
		sensor.updateValues(sensorData)

	def __noVersion(self):
		logging.warning("Could not get firmware version for RF433, force upgrade")
		self.dev.updateFirmware()

	def __version(self, version):
		self.version = version
		logging.info("RF433 version: %i", self.version)
		if version != 12:
			logging.info("Version %i is to old, update firmware", self.version)
			self.dev.updateFirmware()
