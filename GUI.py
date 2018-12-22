import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.messagebox import showerror
import threading
# Teaching 需求
import sys
import os
from configparser import ConfigParser
from Teaching import Teaching
import random
from os import listdir
from os.path import isfile, join

class Application(tk.Tk):
	handler = ''
	labelframe = ''
	
	def __init__(self):
		super().__init__()
		self.createUI()
	
	# 設定函數
	def setting(self):
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

	# 主程式
	def start(self):	
		# init
		os.system("cls")
		cfg = ConfigParser()
		cfg.read('config.ini')
		try:
			login_acc = cfg['save']['username']
			login_pwd = cfg['save']['password']
		except (KeyError):
			self.setting()
		self.handler = Teaching(login_acc, login_pwd)
		handler = self.handler
		
		self.courses_id = []
		self.courses = handler.getCourses()
		self.courses_list_box.delete(0,tk.END)
		for course_num, course_nam in self.courses.items():
			self.courses_list_box.insert('end', course_nam)
			self.courses_id.append(course_num)
		
		self.update()
		
		return 0

		self.hw_id = []
		self.hw = []
		# self.hw = handler.getHomeWorks()
		for crsno, hws in self.hw.items():
			for hw in hws:
				self.homework_list_box.delete(0,tk.END)
				self.homework_list_box.insert('end', "{0} - {1}".format(self.courses[crsno], hw['title']) )
				self.hw_id.append("homeworkID")		
		
		print(self.hw.items())
		# for hw_num, hw_nam in self.hw.items():
			# self.courses_list_box.insert('end', course_nam)
			# self.courses_id.append(course_num)
		
		
		return 0
		
		# handler.getHomeWorks()
		
		# print(courses)
		# handler.downloadFiles(False)

		for crsno, crsname in courses.items():
			files = handler.getFiles(crsno)
			# print(files)
			handler.downloadFiles(files)
		
		
		
		# handler.test()
		return 0

	def about(self):
		print("Debug: 進入About")
		sys.exit()


	def createUI(self):
		# self.= tk.Tk()
		self.title('NKFUST')
		self.geometry('600x400')

		menubar = tk.Menu(self)
		
		filemenu = tk.Menu(menubar, tearoff=0)
		filemenu.add_command(label='New', command=None)
		filemenu.add_command(label='Open', command=None)
		filemenu.add_command(label='Save', command=None)
		filemenu.add_separator()
		filemenu.add_command(label='Exit', command=self.quit)

		editmenu = tk.Menu(menubar, tearoff=0)
		editmenu.add_command(label='Cut', command=None)
		editmenu.add_command(label='Copy', command=None)
		editmenu.add_command(label='Paste', command=None)

		Helpmenu = tk.Menu(menubar, tearoff=0)
		Helpmenu.add_command(label='about', command=self.setting)

		# menubar.add_cascade(label='File', menu=filemenu)
		# menubar.add_cascade(label='Edit', menu=editmenu)
		# menubar.add_cascade(label='Help', menu=Helpmenu)
		menubar.add_command(label='Setting', command=self.setting)
		menubar.add_command(label='About', command=self.about)

		self.config(menu=menubar)

		self.labelframe = tk.LabelFrame(self, text="目前學年度: 107學年度/上學期", labelanchor='n')
		self.labelframe.pack(fill="both", expand="yes")

		course_label = tk.Label(self.labelframe, text='所有課程')
		course_label.grid(row=0, column=0)
		teach_label = tk.Label(self.labelframe, text='教材')
		teach_label.grid(row=0, column=1)
		HW_label = tk.Label(self.labelframe, text='作業')
		HW_label.grid(row=0, column=2)
		
		# Course listbox
		self.courses_list_box = tk.Listbox(self.labelframe, selectmode='SINGLE', width=26, height=15)
		self.courses_list_box.bind('<<ListboxSelect>>', self.select_course)
		self.courses_list_box.grid(row=1, column=0, padx=5, pady=5)

		# Teach listbox
		self.files_list_box = tk.Listbox(self.labelframe, selectmode='MULTIPLE', width=26, height=15)
		self.files_list_box.bind('<<ListboxSelect>>', self.onselect)
		self.files_list_box.grid(row=1, column=1, padx=5, pady=5)

		# HW listbox
		self.homework_list_box = tk.Listbox(self.labelframe, selectmode='MULTIPLE', width=26, height=15)
		self.homework_list_box.bind('<<ListboxSelect>>', self.onselect)
		self.homework_list_box.grid(row=1, column=2, padx=5, pady=5)
		
		# Update teach button
		# update_teach_button = tk.Button(self.labelframe, text='更新教材')
		# update_teach_button.grid(row=2, column=0, padx=5, pady=5)

		# Setting Button
		update_Hw_button = tk.Button(self.labelframe, text='帳號登入', command=lambda :self.thread_it(self.start))
		update_Hw_button.grid(row=2, column=0, padx=5, pady=5)

		# Download teach button
		download_teach_button = tk.Button(self.labelframe, text='下載所選教材', command=None)
		download_teach_button.grid(row=2, column=1)

		# Upload HW button
		upload_Hw_button = tk.Button(self.labelframe, text='上傳所選作業', state='disabled', command=None)
		upload_Hw_button.grid(row=2, column=2)
		return 0

	# Select Course
	def select_course(self, evt):
		sel_course = self.courses_list_box.curselection()
		if (not sel_course):
			return 0
		handler = self.handler
		# Note here that Tkinter passes an event object to onselect()
		self.files_list_box.delete(0,tk.END)
		crsno = self.courses_id[ sel_course[0] ]
		files = handler.getFiles(crsno)
		for file in files:
			self.files_list_box.insert('end', file['title'])
		
		return 0
		if sel_course:
			value = self.courses_list_box.get(sel_course[0])
			print("Selectd Course:" + value)
			self.files_list_box.insert(0, value)
			course_items = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k']
			for course in course_items:
				self.files_list_box.insert('end', course)
			
			self.homework_list_box.insert(0, value)
		
		return 0
	
	# listbox mouse click event
	def onselect(self, evt):
		# Note here that Tkinter passes an event object to onselect()
		sel_teach = self.files_list_box.curselection()
		sel_hw = self.homework_list_box.curselection()
		# download_teach_button.config(state='active')
		# upload_Hw_button.config(state='active')
		if sel_teach:
			print(sel_teach[0])
		elif sel_hw:
			print(sel_hw[0])
		return 0


	# Upload file
	def upload_file(self):
		f_name = askopenfilename(filetypes=(("doc files", "*.doc;*.docx"), ("pdf files", "*.pdf"), ("All files", "*.*")))
		sel_hw = lb3.curselection()
		if f_name:
			try:
				print('上傳:' + lb2.get(sel_hw[0]))
			except:  # <- naked except is a bad idea
				showerror("Open Source File", "Failed to read file\n'%s'" % f_name)
			return

	# Download file
	def download_file(self):
		f_name = asksaveasfilename(filetypes=(("doc files", "*.doc;*.docx"), ("pdf files", "*.pdf"), ("All files", "*.*")))
		sel_teach = lb2.curselection()
		if f_name:
			try:
				print('下載' + lb3.get(sel_teach[0]))
			except:  # <- naked except is a bad idea
				showerror("Open Source File", "Failed to read file\n'%s'" % f_name)
			return

	def loop(self):
		self.window.after(1000, self.start)
		self.window.mainloop()

	@staticmethod
	def thread_it(func, *args):
		t = threading.Thread(target=func, args=args)
		t.setDaemon(True)
		t.start()
		# t.join() # untested

if __name__ == '__main__':
	print("Debug: 進入Main")
	app = Application()
	app.mainloop()