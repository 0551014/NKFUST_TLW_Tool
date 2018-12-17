import sys
import os
from configparser import ConfigParser
from Teaching import Teaching
import random
from os import listdir
from os.path import isfile, join

def setting():
	print('Debug: 進入設定模式')
	key = []
	for i in range(1,100):
		key.append(random.randint(65,90))
	
	print(str(bytearray(key)))
	# login_acc = input('acc')
	# os.system("cls")
	# login_pwd = input('pwd')
	# os.system("cls")
	sys.exit()
	return 0

def main():
	os.system("cls")
	cfg = ConfigParser()
	cfg.read('config.ini')
	try:
		login_acc = cfg['save']['username']
		login_pwd = cfg['save']['password']
	except (KeyError):
		setting()
	
	handler = Teaching(login_acc, login_pwd)
	
	courses = handler.getCourses()
	# handler.getHomeWorks()
	
	# print(courses)
	# handler.downloadFiles(False)

	for crsno, crsname in courses.items():
		files = handler.getFiles(crsno)
		# print(files)
		handler.downloadFiles(files)
	
	
	
	# handler.test()
	sys.exit()
	return 0

if __name__ == '__main__':
	main()