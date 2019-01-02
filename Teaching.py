import sys, os
from tkinter import ttk
import requests
import urllib.request
from urllib import parse
from bs4 import BeautifulSoup
import sys
import re # 規則運算式
from configparser import ConfigParser


class Teaching:
	WEBROOT = 'http://teaching.nkfust.edu.tw/'
	SESSION = ''
	ACCOUNT = ''
	PASSWRD = ''
	HTTPRES = ''
	
	#Config
	cfg = ''
	filepath = ''
	
	#學期資訊
	currentAcy = ''
	currentSem = ''
	courses    = {}
	homeworks  = {}
	
	def __init__(self, login_acc, login_pwd):
		print("Debug: INIT Class-Teaching")
		self.is_logined = False
		self.ACCOUNT = login_acc
		self.PASSWRD = login_pwd
		# Config init
		self.cfg = ConfigParser()
		self.cfg.read('config.ini')
		try:
			self.filepath = self.cfg['default']['path']
		except (KeyError):
			print("Error: Config 格式錯誤")
			sys.exit()
		try:
			if (not os.path.exists(self.filepath)):
				os.makedirs(self.filepath)
			open(os.path.join(self.filepath, 'FILE'), 'a').close()
		except (FileNotFoundError, PermissionError):
			print("Error: 請確認檔案路徑是否正確(或無權存取)")
			sys.exit()
		self.login()

	def login(self):
		print('Info : 進入登入程序')

		ASPSession = ['__EVENTTARGET','__EVENTARGUMENT','__VIEWSTATE','__VIEWSTATEGENERATOR','__PREVIOUSPAGE','__EVENTVALIDATION']
		headers = {
			'Content-Type': 'application/x-www-form-urlencoded',
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
			'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
			'Referer': 'http://teaching.nkfust.edu.tw/Course/Login.aspx',
			'Accept-Encoding': 'gzip, deflate'
		}
		
		self.SESSION = requests.session()
		self.SESSION.headers = headers
		self.HTTPRES = self.SESSION.get(self.WEBROOT + 'course/login.aspx')
		soup = BeautifulSoup(self.HTTPRES.text, "html.parser")
		
		# 登入欄位，ASP需求欄位
		requestForm = {}
		for id in ASPSession:
			field = soup.find(id=id)
			if(field):
				requestForm[id] = field.get('value')
			else:
				print('Error: 網站錯誤. 原因: 欄位異常(' + id + ')')
				sys.exit()
		requestForm['Login1$LoginButton.x'] = 0
		requestForm['Login1$LoginButton.y'] = 0
		requestForm['Login1$UserName'] = self.ACCOUNT
		requestForm['Login1$Password'] = self.PASSWRD
		print('Debug: 頁面正常，登入中...')
		
		# 發送POST請求
		self.HTTPRES = self.SESSION.post(self.WEBROOT + 'course/login.aspx', data=requestForm, headers=headers)
		
		# 獲取登入狀態
		soup = BeautifulSoup(self.HTTPRES.text, "html.parser")
		acyResp = soup.find(id='Label_Work_Acy')
		if (acyResp):
			m = re.match('工作學年度：(\d+)學年度/([上下])學期', acyResp.text.strip())
			self.currentAcy = m.group(1)
			self.currentSem = m.group(2)
			self.is_logined = True
			print('Info : 登入成功！')
			print('Info : 目前為' + self.currentAcy + '學年度' + self.currentSem + '學期')
		else:
			self.is_logined = False
			print('Error: 登入失敗！請確認您的帳號或密碼。(HTML元素錯誤)')
			# sys.exit()

	def getCourses(self):
		print("Info : 取得課程列表")
		self.HTTPRES = self.SESSION.get(self.WEBROOT + 'Course/student/student_1.aspx', cookies=self.HTTPRES.cookies)
		try:
			soup = BeautifulSoup(self.HTTPRES.text, "html.parser")
			name = soup.find(id='ContentPlaceHolder_MainContent_Label_Title')
			courseListTable = soup.find(id='ContentPlaceHolder_MainContent_GridView_Show')
			trs = courseListTable.findAll("tr")
			trs.pop(0) # 移除標題
			print('Debug: 發現' + str(len(trs)) + '個課程')
			for tr in trs:
				courseNumber = tr.findAll("td")[1].text.strip()
				courseName   = tr.find(id=re.compile('^ContentPlaceHolder_MainContent_GridView_Show_HyperLink_Course_'))
				# print(courseName.prettify())
				if ("(停修 Course Withdraw)" in courseName.prettify()):
					courseName = courseName.prettify().split('<font color="red">')[1].split('<br/>')[0].strip() # 去除煩人的英文及空格
					courseName = "[停修]" + courseName
				else:
					courseName   = courseName.prettify().split('<br/>')[0].split('\n')[1].strip() # 去除煩人的英文及空格
				print(courseName)
				self.courses[courseNumber]= courseName
		except (AttributeError):
			print('Error: 網頁異常(AttributeError)')
			# sys.exit()
		return self.courses

	def getHomeWorks(self):
		print("Info : 取得作業列表")
		
		for crsno, crsnm in self.courses.items():
			payload = '?origin=~/homework/student/main.aspx?acy=' + self.currentAcy + '&semester=' + self.currentSem + '&crsno=' + crsno +'&crsname=' + crsnm
			self.HTTPRES = self.SESSION.get(self.WEBROOT + 'Course/transfer.aspx' + payload, cookies=self.HTTPRES.cookies)
			soup = BeautifulSoup(self.HTTPRES.text, "html.parser")
			homeWorkListTable = soup.find(id='ContentPlaceHolder_MainContent_GridView_Wcrs_HomeWork')
			trs = homeWorkListTable.findAll("tr")[1:]
			print('Debug: ' + crsno + ': ' + str(len(trs)) + '個作業 - ' + crsnm)
			self.homeworks[crsno] = []
			for tr in trs:
				tds = tr.findAll("td")
				if(tds[7].text.strip() != '已繳 Done'): # 修改這裡以測試所有HW之顯示
					newHW = {'title':tds[1].text.strip(), 'content':tds[2].text.strip(), 'deadline': tds[5].text.strip()}
					self.homeworks[crsno].append(newHW)
			
			# print('Info : 課程'crsno + '--' + crsnm + '作業:')
		has_hw = False
		for crsno, hws in self.homeworks.items():
			for hw in hws:
				has_hw = True
				print('Debug: "' + self.courses[crsno] + '" 未繳作業: ' + hw['title'])
		if (not has_hw):
			print("Debug: 沒有未交作業")
			return {}
		return self.homeworks

	def getFiles(self, crsno):
		print('Info : 列出課程教材: ' + crsno)
		ASPSession = ['__VIEWSTATE','__VIEWSTATEGENERATOR']
		
		# 取得token
		self.HTTPRES = self.SESSION.get(self.WEBROOT + 'Course/materials/CatalogMenu.aspx?stype=S', cookies=self.HTTPRES.cookies)
		soup = BeautifulSoup(self.HTTPRES.text, "html.parser")
		requestForm = {}
		
		for id in ASPSession:
			field = soup.find(id=id)
			if(field):
				requestForm[id] = field.get('value')
			else:
				print('Error: 網站錯誤. 原因: 欄位異常(' + id + ')')
				# sys.exit()
		
		requestForm['__EVENTTARGET'] = "ComboBox_Crsno"
		requestForm['__EVENTARGUMENT'] = '{"Command":"Select","Index":0}'
		requestForm['__ASYNCPOST'] = "true"
		requestForm['ComboBox_Crsno'] = ""
		requestForm['ComboBox_Crsno_ClientState'] = '{"logEntries":[],"value":"' + crsno + '","text":"","enabled":true,"checkedIndices":[],"checkedItemsTextOverflows":false}'
		requestForm['RadScriptManager1'] = 'ComboBox_CrsnoPanel|ComboBox_Crsno'		
		requestForm['RadTreeView_Catalog_ClientState'] = '{"expandedNodes":[],"collapsedNodes":[],"logEntries":[],"selectedNodes":[],"checkedNodes":[],"scrollPosition":0}'
		requestForm['RadAJAXControlID'] = "RadAjaxManager1"
		# 拿RadScriptManager1_TSM參數
		script = soup.find('script', {'src': re.compile(r'\/Course\/Telerik.Web.UI.WebResource.axd?(.*)')})
		if (script):
			m = re.match('(.*)_TSM_CombinedScripts_=(.*)', script.attrs['src'])
			val = parse.unquote_plus(m.group(2))
			if (val):
				requestForm['RadScriptManager1_TSM'] = val
			else:
				print('Error: 網站錯誤. 原因: 欄位異常(拿RadScriptManager1_TSM參數)')
				# sys.exit()
		
		self.HTTPRES = self.SESSION.post(self.WEBROOT + 'Course/materials/CatalogMenu.aspx?stype=S', data=requestForm, cookies=self.HTTPRES.cookies)
		soup = BeautifulSoup(self.HTTPRES.text, "html.parser")
		results = soup.find(id='RadTreeView_Catalog')
		files = results.findAll("a", {'class':'rtIn'})
		
		fileData = []
		try:
			# 檢查標題是否與請求課程相同
			m = re.match('(\d+)', files[0].text)
			if (m.group(1) == crsno):
				files.pop(0) # 移除標題
				for f in files:
					# print('檔名:' + f.attrs['title'] + '網址:' + f.attrs['href'])
					nf = {'title':f.attrs['title'], 'url':f.attrs['href']}
					fileData.append(nf)
				print('Debug: 找到' + str(len(fileData)) + '個檔案')
				return fileData
			else:
				return []
		except (KeyError, AttributeError):
			print('Error: 網站錯誤. 原因: 欄位異常(RadTreeView_Catalog)')
			sys.exit()

	def downloadFiles(self, files, labelframe, progress_file, progress_total):
		print('Info : 下載 ' + str(len(files)) + ' 個檔案')
		total_file_count = len(files)
		downloaded_count = 1
		#逐一下載檔案
		for file in files:
			progress_total['value'] = downloaded_count / total_file_count * 100
			labelframe.update()
			if ( not file['url'].startswith('./CatalogView.aspx?') ):
				print('Error: Download URL error')
				continue
			get = file['url'].split('./CatalogView.aspx?', 1)[1]
			crsno = get.split('crsno=', 1)[1].split('&', 1)[0]
			crsname = self.courses[crsno]			
			with self.SESSION.get(self.WEBROOT + 'Course/materials/CatalogView.aspx?' + get, cookies=self.HTTPRES.cookies, stream=True) as r:
				if (not 'Content-Length' in r.headers or not 'Content-Disposition' in r.headers):
					print('Error: Download response error(Content-Length)')
					# continue
				# if ( not r.headers['Content-Disposition'].startswith('attachment; filename=') ):
				if ( "filename=" not in r.headers['Content-Disposition'] ):
					print('Error: Download response error(Content-Disposition)')
					continue
				file_size = int(r.headers['Content-Length'])
				file_name = r.headers['Content-Disposition'].split('filename=', 1)[1]
				file_name = parse.unquote(file_name)
				
				#串目錄和檔案
				dest = "{0}\\{1}-{2}-{3}".format(self.filepath, self.currentAcy, crsno, crsname)

				if ( not os.path.exists(dest) ):
					os.makedirs(dest)
				dest_file = os.path.join(dest, file_name)
				#檢查檔案存在
				if  os.path.exists(dest_file):
					debug_message = "Debug: [{0:2}/{1:2}] {2:>8} [Exixts.]{3}".format(downloaded_count, total_file_count, file_size, file_name)
					print(debug_message)
					downloaded_count += 1
					progress_file['value'] = 100
					labelframe.update()
					continue
				#開始下載檔案
				with open(dest_file, 'wb') as f:
					debug_message = "Debug: [{0:2}/{1:2}] ".format(downloaded_count, total_file_count)
					
					file_size_dl = 0
					block_sz = 8192
					while True:
						buffer = r.raw.read(block_sz)
						if not buffer:
							break
				
						file_size_dl += len(buffer)
						f.write(buffer)
				
						status = debug_message + "{:>8}".format(file_size_dl)
						if file_size:
							status += " [{0:6.2f}%]".format(file_size_dl * 100 / file_size)
						status += file_name
						status += chr(13)
						print(status, end="")
						progress_file['value'] = file_size_dl * 100 / file_size
						labelframe.update()
			print()
			downloaded_count += 1
		return 0
		
		
		
		
		
		
		
		
		
		
		
		
		