import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename, asksaveasfilename, askdirectory
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
	def __init__(self):
		super().__init__()
		self.createUI()
	
	# 選存檔目錄
	def select_dict(self, window, entry_box):
		new_dict = askdirectory(title = "Select Download Dictionary", mustexist = True)
		entry_box.delete(0, tk.END)
		entry_box.insert(0, new_dict)
		window.focus_force()

	#存檔
	def save(self, login_window, account_name, account_password, download_dict):
		# 產生亂數加密資料
		key = []
		for i in range(1, 100):
			key.append(random.randint(65, 90))
		print(str(bytearray(key)))

		if account_name is not '' and account_password is not '':
			# print("Debug: 輸入帳號：{0}, 密碼:{1}, 存檔目錄:{2}".format(account_name, account_password, download_dict))
			# Check dictionary
			try:
			    if (not os.path.exists(download_dict)):
			        os.makedirs(download_dict)
			    open(os.path.join(download_dict, 'FILE'), 'a').close()
			except (FileNotFoundError, PermissionError):
				print("Error: 請確認檔案路徑是否正確(或無權存取)")
				showerror("Error", "請確認檔案路徑是否正確(或無權存取)")
				download_dict = os.path.join(os.getcwd(), 'CourseFiles')
			# Config init
			try:
				cfg = ConfigParser()
				cfg.read('config.ini')
				cfg['default'] = {}
				cfg['save'] = {}
				cfg['default']['path'] = download_dict
				cfg['save']['username'] = account_name
				cfg['save']['password'] = account_password
			except (KeyError):
				print("Error: Config 格式錯誤")
				sys.exit()
			with open('config.ini', 'w') as configfile:
				cfg.write(configfile)
			login_window.destroy()
			self.start()
		else:
			showerror("Error", "請輸入帳號和密碼！")
			login_window.destroy()
			self.destroy()
		return 0

	# 設定函數
	def setting(self):
		print('Debug: 進入設定模式')
		# 登入GUI設計
		login = tk.Tk()
		login.title('登入設定')

		# user information
		tk.Label(login, text='※僅限在職教師及在學學生使用※').grid(row=0, column=1, padx=10, pady=10)
		tk.Label(login, text='Username:').grid(row=1, column=0)
		tk.Label(login, text='Password:').grid(row=2, column=0)
		tk.Label(login, text='Download:').grid(row=3, column=0)

		var_usr_name = tk.StringVar()
		var_usr_pwd = tk.StringVar()
		var_download = tk.StringVar()
		entry_usr_name = tk.Entry(login, textvariable=var_usr_name, show='*')
		entry_usr_pwd = tk.Entry(login, textvariable=var_usr_pwd, show='*')
		entry_download = tk.Entry(login, textvariable=var_download)
		set_download = tk.Button(login, text='設定下載目錄', command=lambda: self.select_dict(login, entry_download))
		entry_usr_pwd.grid(row=2, column=1, padx=10, pady=10)
		entry_usr_name.grid(row=1, column=1, padx=10, pady=10)
		entry_download.grid(row=3, column=1, padx=10, pady=10)
		set_download.grid(row=3, column=2)
		entry_download.insert(0, os.path.join(os.getcwd(), 'CourseFiles'))

		# login button
		btn_login = tk.Button(login, text='儲存設定檔', command=lambda: self.save(login, entry_usr_name.get(), entry_usr_pwd.get(), entry_download.get()))
		btn_login.grid(row=1, column=2, padx=10, pady=10)
		
		login.bind("<Return>",lambda e: self.save(login, entry_usr_name.get(), entry_usr_pwd.get(), entry_download.get()))
		
		login.mainloop()
		return 0

	# 下載
	def download(self):
		handler = self.handler
		download_list = [self.files[i] for i in self.files_list_box.curselection()]
		# print(download_list)
		handler.downloadFiles(download_list, self.labelframe, self.progress_file, self.progress_total)

	# 更新作業列表
	def update_homeworks(self):
		self.HW_label.config(text = '作業(更新中...請稍候)')
		self.update()
		handler = self.handler
		self.hw_id = []
		self.hw = {}
		self.hw = handler.getHomeWorks()
		self.homework_list_box.delete(0, tk.END)
		for crsno, hws in self.hw.items():
			for hw in hws:
				self.homework_list_box.insert('end', "{0} - {1}".format(self.courses[crsno], hw['title']))
				self.hw_id.append("homeworkID")
				self.update()
		if (len(self.hw) == 0):
			self.HW_label.config(text = '作業(已更新): 沒有未交作業~')
		else:
			self.HW_label.config(text = '作業(已更新): 尚有未交作業!')
		self.update()
		# for hw_num, hw_nam in self.hw.items():
		# self.courses_list_box.insert('end', course_nam)
		# self.courses_id.append(course_num)
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
		if (not handler.is_logined):
			self.labelframe.config(text = "登入失敗，請重新登入。")
			self.setting()
			return
		self.labelframe.config(text = "歡迎回來～目前為 {0} 學年度 {1} 學期".format(handler.currentAcy, handler.currentSem))
		self.courses_id = []
		self.courses = handler.getCourses()
		self.courses_list_box.delete(0, tk.END)
		for course_num, course_nam in self.courses.items():
			self.courses_list_box.insert('end', course_nam)
			self.courses_id.append(course_num)

		self.update()
		self.thread_it(self.update_homeworks())
		return 0

	# 關於
	def about(self):
		print("Debug: 進入About")
		about = tk.Tk()
		about.title('About')
		about.resizable(False, False)
		# user information
		tk.Label(about, text='Wrttien by En-Cheng Lin @ NKUST').grid(row=0, column=1, padx=10, pady=10)
		about.mainloop()
		return 0

	# 建立GUI
	def createUI(self):
		# self.= tk.Tk()
		self.title('NKFUST')
		self.geometry('600x400')
		self.resizable(False, False)

		menubar = tk.Menu(self)

		Helpmenu = tk.Menu(menubar, tearoff=0)
		Helpmenu.add_command(label='about', command=self.setting)
		menubar.add_command(label='Setting', command=self.setting)
		menubar.add_command(label='About', command=self.about)

		self.config(menu=menubar)

		self.labelframe = tk.LabelFrame(self, text="請登入", labelanchor='n')
		self.labelframe.pack(fill="both", expand=True)

		course_label = tk.Label(self.labelframe, text='所有課程')
		course_label.grid(row=0, column=0)
		teach_label = tk.Label(self.labelframe, text='教材')
		teach_label.grid(row=0, column=1)
		self.HW_label = tk.Label(self.labelframe, text='作業')
		self.HW_label.grid(row=0, column=3)

		# Course listbox
		self.courses_list_box = tk.Listbox(self.labelframe, selectmode=tk.SINGLE, width=26, height=15)
		self.courses_list_box.bind('<<ListboxSelect>>', self.select_course)
		self.courses_list_box.grid(row=1, column=0, padx=5, pady=5)

		# Teach listbox
		files_list_scrollbar = tk.Scrollbar(self.labelframe, orient=tk.VERTICAL)
		self.files_list_box = tk.Listbox(self.labelframe, selectmode=tk.EXTENDED, yscrollcommand=files_list_scrollbar.set, width=26, height=15)
		self.files_list_box.bind('<<ListboxSelect>>', self.onselect)
		files_list_scrollbar.config(command=self.files_list_box.yview)
		self.files_list_box.grid(row=1, column=1, padx=0, pady=5)
		files_list_scrollbar.grid(row=1, column=2, padx=0, pady=5, sticky='nws')

		# HW listbox
		self.homework_list_box = tk.Listbox(self.labelframe, selectmode=tk.SINGLE, width=26, height=15)
		self.homework_list_box.bind('<<ListboxSelect>>', self.onselect)
		self.homework_list_box.grid(row=1, column=3, padx=5, pady=5)

		# Update teach button
		# update_teach_button = tk.Button(self.labelframe, text='更新教材')
		# update_teach_button.grid(row=2, column=0, padx=5, pady=5)

		# Setting Button
		update_Hw_button = tk.Button(
			self.labelframe, text='帳號登入', command=lambda: self.thread_it(self.start))
		update_Hw_button.grid(row=2, column=0, padx=5, pady=5)

		# Download teach button
		download_teach_button = tk.Button(self.labelframe, text='下載所選教材', command=lambda: self.download())
		download_teach_button.grid(row=2, column=1)

		# Progressbar(File)
		self.progress_file = ttk.Progressbar(self.labelframe, orient=tk.HORIZONTAL, length=150, mode='determinate')
		self.progress_file.grid(row=3, column=1, padx=0, pady=10)

		# Progressbar(Total)
		self.progress_total = ttk.Progressbar(self.labelframe, orient=tk.HORIZONTAL, length=150, mode='determinate')
		self.progress_total.grid(row=4, column=1, padx=0, pady=0)


		# Upload HW button
		# upload_Hw_button = tk.Button(
		# 	self.labelframe, text='上傳所選作業', state='disabled', command=None)
		# upload_Hw_button.grid(row=2, column=3)
		return 0

	# Select Course
	def select_course(self, evt):
		sel_course = self.courses_list_box.curselection()
		if (not sel_course):
			return 0
		handler = self.handler
		# Note here that Tkinter passes an event object to onselect()
		self.files_list_box.delete(0, tk.END)
		crsno = self.courses_id[sel_course[0]]
		self.files = handler.getFiles(crsno)
		for file in self.files:
			self.files_list_box.insert('end', file['title'])

		return 0
		if sel_course:
			value = self.courses_list_box.get(sel_course[0])
			print("Selectd Course:" + value)
			self.files_list_box.insert(0, value)
			course_items = ['a', 'b', 'c', 'd',
							'e', 'f', 'g', 'h', 'i', 'j', 'k']
			for course in course_items:
				self.files_list_box.insert('end', course)

			self.homework_list_box.insert(0, value)

		return 0

	# listbox mouse click event
	def onselect(self, evt):
		self.progress_file['value'] = 0
		self.progress_total['value'] = 0
		return
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
		f_name = askopenfilename(filetypes=(
			("doc files", "*.doc;*.docx"), ("pdf files", "*.pdf"), ("All files", "*.*")))
		sel_hw = lb3.curselection()
		if f_name:
			try:
				print('上傳:' + lb2.get(sel_hw[0]))
			except:  # <- naked except is a bad idea
				showerror("Open Source File",
						  "Failed to read file\n'%s'" % f_name)
			return

	# Download file
	def download_file(self):
		f_name = asksaveasfilename(filetypes=(
			("doc files", "*.doc;*.docx"), ("pdf files", "*.pdf"), ("All files", "*.*")))
		sel_teach = lb2.curselection()
		if f_name:
			try:
				print('下載' + lb3.get(sel_teach[0]))
			except:  # <- naked except is a bad idea
				showerror("Open Source File",
						  "Failed to read file\n'%s'" % f_name)
			return

	@staticmethod
	def thread_it(func, *args):
		t = threading.Thread(target=func, args=args)
		t.setDaemon(True)
		t.start()
		#t.join() # untested

	def loooooooop(self):
		self.thread_it(self.mainloop())

if __name__ == '__main__':
	print("Debug: 進入Main")
	app = Application()
	app.mainloop()
	# app.loooooooop()
