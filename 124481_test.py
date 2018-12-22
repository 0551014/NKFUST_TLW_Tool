import tkinter as tk
from tkinter.filedialog import askopenfilename
from tkinter.messagebox import showerror
from tkinter.ttk import *

window = tk.Tk()
window.title('登入')

# user information
tk.Label(window, text='※僅限在職教師及在學學生使用※').grid(row=0, column=1, padx=10, pady=10)
tk.Label(window, text='Account:').grid(row=1, column=0)
tk.Label(window, text='Password:').grid(row=2, column=0)

var_usr_name = tk.StringVar()
entry_usr_name = tk.Entry(window, textvariable=var_usr_name, show='*')
entry_usr_name.grid(row=1, column=1)
var_usr_pwd = tk.StringVar()
entry_usr_pwd = tk.Entry(window, textvariable=var_usr_pwd, show='*')
entry_usr_pwd.grid(row=2, column=1, padx=10, pady=10)


def usr_login():
    if entry_usr_pwd.get() is not '' or entry_usr_name.get() is not '':
        if entry_usr_name.get() == '123456789' or entry_usr_pwd == '123456789':
            # print(entry_usr_name.get())
            # print(entry_usr_pwd.get())
            window.destroy()
        else:
            showerror('Error', '帳號或密碼錯誤，請重新輸入!')


# login button
btn_login = tk.Button(window, text='Login', command=usr_login)
btn_login.grid(row=1, column=3, padx=10, pady=10)
window.mainloop()


window = tk.Tk()
window.title('教學課程網 teaching and Learning ')

menubar = tk.Menu(window)
filemenu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label='File', menu=filemenu)
filemenu.add_command(label='New', command=None)
filemenu.add_command(label='Open', command=None)
filemenu.add_command(label='Save', command=None)
filemenu.add_separator()
filemenu.add_command(label='Exit', command=window.quit)

editmenu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label='Edit', menu=editmenu)
editmenu.add_command(label='Cut', command=None)
editmenu.add_command(label='Copy', command=None)
editmenu.add_command(label='Paste', command=None)

Helpmenu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label='Help', menu=Helpmenu)
Helpmenu.add_command(label='about')


window.config(menu=menubar)


labelframe = tk.LabelFrame(window, text="目前學年度: 107學年度/上學期", labelanchor='n')
labelframe.pack(fill="both", expand="yes")


course_label = tk.Label(labelframe, text='所有課程')
course_label.grid(row=0, column=0)
teach_label = tk.Label(labelframe, text='教材')
teach_label.grid(row=0, column=2)
HW_label = tk.Label(labelframe, text='作業')
HW_label.grid(row=0, column=4)


# listbox mouse click event
def onselect(evt):
    # Note here that Tkinter passes an event object to onselect()
    sel_course = lb.curselection()
    download_teach_button.config(state='active')
    upload_Hw_button.config(state='active')

    if sel_course:
        lb2.delete(first=0)
        lb3.delete(first=0)
        value = lb.get(sel_course[0])
        lb2.insert(0, value)
        lb3.insert(0, value)


# Course listbox
lb = tk.Listbox(labelframe, selectmode='SINGLE', width=26, height=15)
lb.bind('<<ListboxSelect>>', onselect)
course_items = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'k', 'k', 'k', 'k', 'k', 'k', 'k']
for course in course_items:
    lb.insert('end', course)
lb.grid(row=1, column=0)
lb_scrollbar = tk.Scrollbar(labelframe, orient="vertical")
lb_scrollbar.config(command=lb.yview)
lb_scrollbar.grid(row=1, column=1, sticky='nws')
lb.config(yscrollcommand=lb_scrollbar.set)

# Teach listbox
lb2 = tk.Listbox(labelframe, selectmode='MULTIPLE', width=26, height=15)
lb2.grid(row=1, column=2)
lb2_scrollbar = tk.Scrollbar(labelframe, orient="vertical")
lb2_scrollbar.config(command=lb2.yview)
lb2_scrollbar.grid(row=1, column=3, sticky='nws')
lb2.config(yscrollcommand=lb2_scrollbar.set)

# HW listbox
lb3 = tk.Listbox(labelframe, selectmode='MULTIPLE', width=26, height=15)
lb3.grid(row=1, column=4)
lb3_scrollbar = tk.Scrollbar(labelframe, orient="vertical")
lb3_scrollbar.config(command=lb3.yview)
lb3_scrollbar.grid(row=1, column=5, sticky='nws')
lb3.config(yscrollcommand=lb3_scrollbar.set)


# Upload file
def upload_file():
    f_name = askopenfilename(filetypes=(("doc files", "*.doc;*.docx"), ("pdf files", "*.pdf"), ("All files", "*.*")))
    sel_hw = lb3.curselection()
    if f_name:
        try:
            print('上傳:' + lb3.get(sel_hw[0]))
        except:  # <- naked except is a bad idea
            showerror("Open Source File", "Failed to read file\n'%s'" % f_name)
        return


# Download file
def download_file():
    sel_course = lb2.curselection()
    print(lb2.get(sel_course[0]))
    import time
    for i in range(100):
        progress['value'] = i+1
        labelframe.update_idletasks()
        time.sleep(0.1)


# Download teach button
download_teach_button = tk.Button(labelframe, text='下載所選教材', state='disabled', command=download_file)
download_teach_button.grid(row=2, column=2)

# Upload HW button
upload_Hw_button = tk.Button(labelframe, text='上傳所選作業', state='disabled', command=upload_file)
upload_Hw_button.grid(row=2, column=4)

progress = Progressbar(labelframe, orient=tk.HORIZONTAL, length=200, mode='determinate')
progress.grid(row=3, column=2, padx=10, pady=10)
window.mainloop()
