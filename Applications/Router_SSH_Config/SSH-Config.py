#! /usr/bin/python

#################################################
#  Name : SSH-Config.py
#
#  Description : Used to configure Cisco Router 
#                
#  command line :  -t  <testbed file>
#                  -u  <User Input file>
#                  -c  <configration command file>
#
#  Sample Usage :  SSH-Config.py -t router_ip.txt \
#                                -u router_userpass.txt \
#                                -c  router_config.txt
#########################################################

                  
#############   Import Module #####################
import paramiko
import threading
import os.path
import subprocess
import time 
import sys
import re 
import socket
from  optparse import OptionParser
import Router as RT
################# End #############################

def read_testbed_file (ip_file):
	check=False
	try:
		# Read the testbed file 
		selected_ip_file=open(ip_file, "r")
		
		# Read from the Begining
		selected_ip_file.seek(0)
		
		#Read all the lines from the files
		ip_list=selected_ip_file.read().splitlines()

		#Close the file
		selected_ip_file.close()

		return ip_list 

	except IOError:
		print "File %s is not existing" % ip_file 
def read_user_file (user_file):
	global username 
	global password
	retOut=False 

	try:
		user_input_file=open(user_file,"r")
		user_input_file.seek(0)
		line=user_input_file.readlines()
		username=line[0].split(",")[0]
		password=line[0].split(",")[1].rstrip("\n")
		print "Username = %s " % username
		print "Password = %s " % password 
	except IOError:
		print "File %s is not existing" % user_file

def read_command_file(cmd_file):
	retout=False
        command=""
	try:
		cmd_input_file=open(cmd_file,"r")
		cmd_input_file.seek(0)
		command = cmd_input_file.readlines()
	except IOError:
		print "File %s is not existing" % cmd_file
		return command
	cmd_input_file.close()	
	return command

def valid_ip_address(ip):
	pat=re.compile("^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$")
	ret=pat.match(ip)
	if ret:
		a=ret.group(1)
		b=ret.group(2)
		c=ret.group(3)
		d=ret.group(4)
		if ( (1 <= int(a) <= 223)\
			and (int(a) != 127)\
			and ( 0 <= int(b) <= 255)\
			and ( 0 <= int(c) <= 255)\
			and ( 0 <= int(d) <= 255)):
				print ("Valid IP address %s",ip)
				return True
		else:
			print ("Invalid IP address %s",ip)
			return False
	else:
		return False

		
def Verify_Ip_Addr(ip_list):
	Valid=True
	for ip in ip_list:
		ret=valid_ip_address(ip)
		if (ret):
			continue	
		else:
			Valid=False
			break
	return Valid			

def Verify_Devices_IsReachable(ip_list):
	Valid=True
	for ip in ip_list:
		ping_reply = subprocess.call(['ping', '-c', '2', '-w', '2', '-q', '-n', ip])
		if ping_reply == 0:
			continue
		elif ping_reply == 2:
			Valid=False
			print ("\n No response from the Device %s ",ip)
			break
		else: 
			Valid=False
			print ("\n Ping to the Device Failed %s ", ip)
			break
	return Valid

def Configure_Router(ip_addr):
	Error=True
	uut=RT.Router(ip_addr, username, password)
	uut.Router_Connect()
	configs=read_command_file(cmd_file)
	Error=uut.Router_Config(configs)
	uut.Router_Close()
	return Error
	
	

################# MAIN #################################

#Parse the Command Line Arguments
parser = OptionParser()
parser.add_option("-t", "--testbedfile", dest="ip_file", help="file with all managemnt IP address", metavar="FILE")
parser.add_option("-u", "--userfile", dest="user_file", help="User Data file", metavar="FILE")
parser.add_option("-c", "--commandfile", dest="cmd_file", help="Router Config Command", metavar="FILE")
(options, args)=parser.parse_args()

input_file = options.ip_file
user_file = options.user_file
cmd_file = options.cmd_file

print ("Testbed File = %s User = %s Commands = %s",input_file, user_file, cmd_file) 

# Read The Testbed File 
ip_list = read_testbed_file (input_file)

# Read the User File 
retOut=read_user_file (user_file)


#Verfiy if Valid IP address
retVal= Verify_Ip_Addr (ip_list)
if (retVal == False):
	print ("\n InValid IP Address in the Testbedfile %s",input_file)
	sys.exit(0)

#Verify the reachablity of the device
retVal = Verify_Devices_IsReachable(ip_list)
if (retVal == False):
	print ("\n Verify the network topology ")
	sys.exit(0)

#Configure all the Routers
for ip in ip_list:
	Error=Configure_Router(ip)
	
print Error



