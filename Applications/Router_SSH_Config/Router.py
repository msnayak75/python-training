#! /usr/bin/python

import re
import sys
import paramiko
import os 
import subprocess
import time
import sys

class Router(object):
	def __init__(self, mgmt_ip, username, password):
		self.router_mgmtip = mgmt_ip
		self.uname = username
		self.pword = password
		self.session = 0
		self.connection = ""
		self.connect = False 
	
	def get_RouterIp(self):
		return self.router_mgmtip

        def Router_Connect(self):
		try:
			self.session = paramiko.SSHClient()
                	self.session.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                	self.session.connect(self.router_mgmtip, username=self.uname, password=self.pword)
                	self.connection = self.session.invoke_shell()
			self.connect = True
                	self.connection.send("terminal length 0\n")
                	time.sleep(1)
			routput=self.connection.recv(65535)
			print routput
			if re.search(r"% Invalid input dectected at", routput):
				print ("IOS Syntax Error") 
		except paramiko.AuthenticationException:
                	print "Invalid UserName or Password"

	def Router_Close(self):
		self.session.close()

	def Router_Config(self, configs):
		Error=True
		if (self.connect == False):
			print (" No Connection is Established \n")
			return Error
		#get router to config mode
		self.connection.send("configure terminal \n")
		for line in configs:
			self.connection.send(line)
			time.sleep(1)
			routput=self.connection.recv(65535)
			if re.search(r"% Invalid input detected at", routput):
				print ("IOS Syntax Error %s",line) 
				print routput
				return Error
			print routput
			Error=False
		self.connection.send("exit \n")
		return Error

	def Router_Show(self, show_cmd):
		Error=False
		if (self.connect == False):
			print (" No Connection is Established \n")
			return Error
		cmd=show_cmd + " \n"
		self.connection.send(cmd)
		time.sleep(1)
		routput=self.connection.recv(65535)
		if re.search(r"% Invalid input detected at", routput):
			print ("IOS Syntax Error %s",show_cmd) 
			return Error
		print routput
		Error=True
		return Error

