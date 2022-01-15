from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.modalview import ModalView
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg as FCK
from kivy.core.window import Window
from kivy.uix.dropdown import DropDown
from kivy.uix.filechooser import FileChooserListView
from kivy.factory import Factory
from kivy.properties import ListProperty, ObjectProperty

from collections import OrderedDict
from utils.datatable import DataTable
import utils.camera as cam
import mysql.connector
from datetime import datetime
import hashlib
import pandas as pd
import matplotlib.pyplot as plt
from threading import Thread,Timer
import time
from cv2 import cv2
import os




Window.size = (1200, 700)
# Builder.load_file('admin/admin.kv')

file_path = ''
for_once = False
running = False

class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)
    
class Notify(ModalView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (.7,.7)

class MultiSelectSpinner(Button):
    """Widget allowing to select multiple text options."""

    dropdown = ObjectProperty(None)
    """(internal) DropDown used with MultiSelectSpinner."""

    values = ListProperty([])
    """Values to choose from."""

    selected_values = ListProperty([])
    """List of values selected by the user."""

    def __init__(self, **kwargs):
        self.bind(dropdown=self.update_dropdown)
        self.bind(values=self.update_dropdown)
        super(MultiSelectSpinner, self).__init__(**kwargs)
        self.bind(on_release=self.toggle_dropdown)

    def toggle_dropdown(self, *args):
        if self.dropdown.parent:
            self.dropdown.dismiss()
        else:
            self.dropdown.open(self)

    def update_dropdown(self, *args):
        if not self.dropdown:
            self.dropdown = DropDown()
        values = self.values
        if values:
            if self.dropdown.children:
                self.dropdown.clear_widgets()
            for value in values:
                b = Factory.MultiSelectOption(text=value)
                b.bind(state=self.select_value)
                self.dropdown.add_widget(b)

    def select_value(self, instance, value):
        if value == 'down':
            if instance.text not in self.selected_values:
                self.selected_values.append(instance.text)
        else:
            if instance.text in self.selected_values:
                self.selected_values.remove(instance.text)

    def on_selected_values(self, instance, value):
        if value:
            self.text = ', '.join(value)
        else:
            self.text = ''

class AdminWindow(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mydb = mysql.connector.connect(
            host = 'localhost',
            user='root',
            passwd='',
            database='test'
        )
        self.mycursor = self.mydb.cursor()
        self.notify = Notify()

        #Display Products in analysis
        mycursor1 = self.mydb.cursor()
        sql = 'SELECT * FROM product'
        mycursor1.execute(sql)
        products = mycursor1.fetchall()

        product_code = []
        product_name = []
        spinvals = []
        for product in products:
            product_code.append(product[0])
            name = product[1]
            if len(name)>30:
                name = name[:30] + '...'
            product_name.append(name)

        for x in range(len(product_code)):
            line = ' | '.join([product_code[x],product_name[x]])
            spinvals.append(line)
        # self.ids.target_product.values = spinvals

        #Display departments in spinner
        mycursor2 = self.mydb.cursor()
        sql = 'SELECT * FROM department'
        mycursor2.execute(sql)
        departments = mycursor2.fetchall()

        department_id = []
        department_name = []
        spinvals_department = []
        for department in departments:
            department_id.append(department[0])
            name_d = department[1]
            department_name.append(name_d)

        for x in range(len(department_id)):
            line_d = ' | '.join([str(department_id[x]),department_name[x]])
            spinvals_department.append(line_d)
        self.ids.target_department.values = spinvals_department
        self.ids.target_product.values = spinvals_department

        #Diplay cameras with departments
        mycursor3 = self.mydb.cursor()
        sql_cam = 'SELECT * FROM cameras'
        mycursor3.execute(sql_cam)
        cameras_list = mycursor3.fetchall()

        camera_id = []
        camera_department = []
        spinvals_camera = []
        for camera_d in cameras_list:
            camera_id.append(camera_d[0])
            camera_department.append(camera_d[1])

        for y in range(len(camera_id)):
            line_c = ' | '.join([str(camera_department[y]),str(camera_id[y])])
            spinvals_camera.append(line_c)
        self.ids.target_detection_department.values = spinvals_camera

        #Display Users
        content = self.ids.scrn_contents
        users = self.get_users()
        userstable = DataTable(table=users)
        content.add_widget(userstable)

        #Display Products
        product_scrn = self.ids.scrn_product_contents
        products = self.get_products()
        prod_table = DataTable(table=products)
        product_scrn.add_widget(prod_table)

        #Display Cameras
        camera_scrn = self.ids.scrn_camera_contents
        cameras = self.get_camera()
        cam_table = DataTable(table=cameras)
        camera_scrn.add_widget(cam_table)

        #Display Schedules
        detection_scrn = self.ids.scrn_detection_contents
        schedules = self.get_schedules()
        sch_table = DataTable(table=schedules)
        detection_scrn.add_widget(sch_table)

        #Display Presence
        presence_scrn = self.ids.scrn_presence_contents
        presence = self.get_presence()
        presence_table = DataTable(table=presence)
        presence_scrn.add_widget(presence_table)

        #Display Absence
        absence_scrn = self.ids.scrn_absence_contents
        absence = self.get_absence()
        absence_table = DataTable(table=absence)
        absence_scrn.add_widget(absence_table)

    def change_screen(self, instance):
        if instance.text == 'Manage Departments':
            self.ids.scrn_mngr.current = 'scr_product_content'

        elif instance.text == 'Main Window':
            self.ids.scrn_mngr.current = 'scrn_menu'

        elif instance.text == 'Manage Users':
            self.ids.scrn_mngr.current = 'scrn_content'

        elif instance.text == 'Manage Cameras':
            self.ids.scrn_mngr.current = 'scr_camera_content' 

        elif instance.text == 'Face Detection':
            self.ids.scrn_mngr.current = 'scr_detection_content' 

        elif instance.text == 'Current Session':
            self.ids.scrn_mngr.current = 'scrn_presence_content' 

        elif instance.text == 'Absence List':
            self.ids.scrn_mngr.current = 'scrn_absence_content' 

        else:
            self.ids.scrn_mngr.current = 'scrn_analysis'

    def view_stats(self):
        plt.cla()
        target_product = self.ids.target_product.text 
        target = target_product[:target_product.find(' | ')]
        name = target_product[target_product.find(' | '):]
        print (target)

        df = pd.read_csv('C:/Users/trator979/Desktop/Python_Java/PythonKivy/ptestfile.csv')
        absence = []
        dates = []
        count = 0
        for x in range(len(df)):
            if str(df.department_id[x]) == target:
                dates.append(df.absence_date[x])
                absence.append(count)
                count += 1
        plt.bar(dates,absence,color='teal',label=name)
        plt.ylabel('Absence')
        plt.xlabel('Date')

        self.ids.analysis_res.add_widget(FCK(plt.gcf()))

    def view_stats_department(self):

        target_department = self.ids.target_department.text 
        target = target_department[:target_department.find(' | ')]
        name = target_department[target_department.find(' | '):]
        
        print ('-----'+target+'-----')

        content = self.ids.scrn_product_contents
        content.clear_widgets()
        prods = self.get_employees_department(target)
        stocktable = DataTable(table=prods)
        content.add_widget(stocktable)

    def killwsitch (self,dtx):
        self.notify.dismiss()
        self.notify.clear_widgets()

    def logout(self):
        self.parent.parent.current = 'scrn_si'

    #===========================Presence List================================

    def get_presence(self):
        mydb = mysql.connector.connect(
            host = 'localhost',
            user='root',
            passwd='',
            database='test'
        )
        mycursor = mydb.cursor()

        _presence= OrderedDict()
        
        _presence['Cin Number'] = {}
        _presence['First Name'] = {}
        _presence['Last Name'] = {}
        _presence['Department ID'] = {}
        _presence['State'] = {}
        _presence['Absence Date'] = {}

        cin_number = []
        first_name = []
        last_name = []
        department_id = []
        state = []
        absence_date = []

        sql = 'SELECT * FROM presence'
        mycursor.execute(sql)
        presence = mycursor.fetchall()

        for user in presence:
            cin_number.append(user[0])
            first_name.append(user[1])
            last_name.append(user[2])
            department_id.append(user[3])
            state.append(user[4])
            absence_date.append(user[5])

        users_length = len(cin_number)
        idx = 0 
        while idx < users_length:
            _presence['Cin Number'][idx] = cin_number[idx]
            _presence['First Name'][idx] = first_name[idx]
            _presence['Last Name'][idx] = last_name[idx]
            _presence['Department ID'][idx] = department_id[idx]
            _presence['State'][idx] = state[idx]
            _presence['Absence Date'][idx] = absence_date[idx]
            idx += 1
        return _presence
       
    def delete_presence(self):
        sql = 'DELETE FROM presence'
        self.mycursor.execute(sql)
        self.mydb.commit()
        print ("presence list deleted ...")

        content = self.ids.scrn_presence_contents
        content.clear_widgets()
        presence = self.get_presence()
        presence_table = DataTable(table=presence)
        content.add_widget(presence_table)

    #===========================Absence List=================================

    def get_absence(self):
        mydb = mysql.connector.connect(
            host = 'localhost',
            user='root',
            passwd='',
            database='test'
        )
        mycursor = mydb.cursor()

        _absence= OrderedDict()
        
        _absence['Cin Number'] = {}
        _absence['First Name'] = {}
        _absence['Last Name'] = {}
        _absence['Department ID'] = {}
        _absence['State'] = {}
        _absence['Absence Date'] = {}

        cin_number = []
        first_name = []
        last_name = []
        department_id = []
        state = []
        absence_date = []

        sql = 'SELECT * FROM absence'
        mycursor.execute(sql)
        absence = mycursor.fetchall()

        for user in absence:
            cin_number.append(user[0])
            first_name.append(user[1])
            last_name.append(user[2])
            department_id.append(user[3])
            state.append(user[4])
            absence_date.append(user[5])

        users_length = len(cin_number)
        idx = 0 
        while idx < users_length:
            _absence['Cin Number'][idx] = cin_number[idx]
            _absence['First Name'][idx] = first_name[idx]
            _absence['Last Name'][idx] = last_name[idx]
            _absence['Department ID'][idx] = department_id[idx]
            _absence['State'][idx] = state[idx]
            _absence['Absence Date'][idx] = absence_date[idx]
            idx += 1
        return _absence

    #===========================Time and Functionalities=====================
    
    def runStuff(self):
        print("Started")

        mydb = mysql.connector.connect(
            host = 'localhost',
            user='root',
            passwd='',
            database='test'
        )
        mycursor = mydb.cursor()
        sql = 'SELECT * FROM schedule'
        mycursor.execute(sql)
        sessions = mycursor.fetchall()
        
        for session in sessions:
            date_time_obj = datetime.strptime(session[0], '%H:%M')
            x=datetime.today()
            y=x.replace(day=x.day, hour=date_time_obj.hour, minute=date_time_obj.minute, second=0, microsecond=0)
            delta_t=y-x

            secs=delta_t.seconds+1
            print(secs)

            t1 = Timer(secs, self.create_presence_list)
            t2 = Timer(secs, self.detection_run)
            t1.start()
            t2.start()

            date_time_end = datetime.strptime(session[1], '%H:%M')
            y_end = x.replace(day=x.day, hour=date_time_end.hour, minute=date_time_end.minute, second=0, microsecond=0)
            delta_t_end=y_end-x
            secs_to_end=delta_t_end.seconds+1

            t1_end = Timer(secs_to_end, self.copy_to_stock)
            t2_end = Timer(secs_to_end+10, self.delete_presence)
            t1_end.start()
            t2_end.start()

    def Hourly_sessions(self):
        
        mydb = mysql.connector.connect(
            host = 'localhost',
            user='root',
            passwd='',
            database='test'
        )
        mycursor = mydb.cursor()
        sql = 'SELECT * FROM schedule'
        mycursor.execute(sql)

        sessions = mycursor.fetchall()
        for session in sessions:
            now = datetime.now()
            hour = '{:02d}'.format(now.hour)
            minute = '{:02d}'.format(now.minute)
            TimeNow = '{}:{}'.format(hour, minute)
            if session[0] == TimeNow:
                print('Creating Presence list ...')
                self.create_presence_list()
                print ('Presence list created.')
                self.detection_run()
                global for_once 
                for_once = True
            if session[1] == TimeNow:
                if for_once == True:
                    self.copy_to_stock()
                    for_once = False
                self.delete_presence()

    def create_presence_list(self):
        mydb = mysql.connector.connect(
            host = 'localhost',
            user='root',
            passwd='',
            database='test'
        )
        mycursor = mydb.cursor()
        sql = 'SELECT * FROM employee'
        mycursor.execute(sql)
        result = mycursor.fetchall()
        print('Creating Presence list ...')
        for employee in result:
            cin = employee[1]
            first_name = employee[2]
            last_name = employee[3]
            dep_id = employee[8]
            state = 'absent'
            sql_presence = 'INSERT INTO presence(cin_number,first_name,last_name,department_id,state,absence_date) Values(%s,%s,%s,%s,%s,%s)'
            values = [cin,first_name,last_name,dep_id,state,datetime.now()]
            self.mycursor.execute(sql_presence,values)
            self.mydb.commit()

        content = self.ids.scrn_presence_contents
        content.clear_widgets()
        absence = self.get_presence()
        absence_table = DataTable(table=absence)
        content.add_widget(absence_table)
 
    def copy_to_stock(self):
        mydb = mysql.connector.connect(
            host = 'localhost',
            user='root',
            passwd='',
            database='test'
        )
        mycursor = mydb.cursor()

        print ("moving employees to absence list ...")
        presence = 'absent'
        sql = 'INSERT INTO absence SELECT * FROM presence where state = %s'
        values = [presence]
        mycursor.execute(sql,values)
        mydb.commit()

    def detection_run(self):

        mydb = mysql.connector.connect(
            host = 'localhost',
            user='root',
            passwd='',
            database='test'
        )
        mycursor = mydb.cursor()

        sql = 'SELECT * FROM cameras'
        mycursor.execute(sql)
        departments = mycursor.fetchall()
        th = []
        for dep in departments:

            encode = cam.picencode(str(dep[1]))
            names = cam.readname(str(dep[1]))

            detect = cam.camThread("Cam"+str(dep[0]),dep[0],encode,names)
            th.append(detect)
        for thread in th:
            thread.start()

    #===========================Schedule Functions===============================

    def view_stats_detection(self):

        target_detection = self.ids.target_detection_department.text 
        target = target_detection[:target_detection.find(' | ')]
        name = target_detection[target_detection.find(' | '):]

        print ('Starting face detection '+target)
        
        encode = cam.picencode(str(target))
        names = cam.readname(str(target))
        detect = cam.camThread("Main Cam",0,encode,names)
        detect.start()

    def add_schedule_field(self):
        target = self.ids.ops_fields_d
        target.clear_widgets()

        curd_start = TextInput(hint_text="Start Time")
        curd_end = TextInput(hint_text="End Time")
        crud_submit = Button(text='Add',size_hint_x=None,width=100,on_release=lambda x:
        self.add_schedule(curd_start.text,curd_end.text))

        target.add_widget(curd_start)
        target.add_widget(curd_end)
        target.add_widget(crud_submit)

    def add_schedule(self,start_time,end_time):
        if start_time == '' or end_time == '' :
            self.notify.add_widget(Label(text='[color=#FF0000][b]All Fields Required[/b][/color]',markup=True))
            self.notify.open()
            Clock.schedule_once(self.killwsitch,1)
        else:
            sql = 'INSERT INTO schedule(start_time,end_time) Values(%s,%s)'
            values = [start_time,end_time]
            self.mycursor.execute(sql,values)
            self.mydb.commit()
            content = self.ids.scrn_detection_contents
            content.clear_widgets()

            schedules = self.get_schedules()
            scheduletable = DataTable(table=schedules)
            content.add_widget(scheduletable)

    def remove_schedule_field(self):
        target = self.ids.ops_fields_d
        target.clear_widgets()
        crud_time = TextInput(hint_text='Start Time')
        crud_submit = Button(text='Remove',size_hint_x=None,width=100,on_release=lambda x:
        self.remove_schedule(crud_time.text))

        target.add_widget(crud_time)
        target.add_widget(crud_submit)

    def remove_schedule(self,start_t):

        if start_t == '':
            self.notify.add_widget(Label(text='[color=#FF0000][b]All Fields Required[/b][/color]',markup=True))
            self.notify.open()
            Clock.schedule_once(self.killwsitch,1)
        else:
            sql = 'DELETE FROM schedule WHERE start_time = %s'
            values = [start_t]
            self.mycursor.execute(sql,values)
            self.mydb.commit()
            content_sch = self.ids.scrn_detection_contents
            content_sch.clear_widgets()

            schedules = self.get_schedules()
            scheduletable = DataTable(table=schedules)
            content_sch.add_widget(scheduletable)

    def get_schedules(self):
        mydb = mysql.connector.connect(
            host = 'localhost',
            user='root',
            passwd='',
            database='test'
        )
        mycursor = mydb.cursor()

        _schedules= OrderedDict()
        
        _schedules['Start Time'] = {}
        _schedules['End Time'] = {}

        start_time = []
        end_time = []

        sql = 'SELECT * FROM schedule'
        mycursor.execute(sql)
        schedules = mycursor.fetchall()

        for user in schedules:
            start_time.append(user[0])
            end_time.append(user[1])

        users_length = len(start_time)
        idx = 0 
        while idx < users_length:
            _schedules['Start Time'][idx] = start_time[idx]
            _schedules['End Time'][idx] = end_time[idx]
            idx += 1
        return _schedules

    #===========================Camera Functions=============================

    def returnCameraIndexes(self):
            # checks the first 10 indexes.
            index = 0
            arr = []
            i = 2
            while i > 0:
                cap = cv2.VideoCapture(index)
                if cap.read()[0]:
                    x = str(index)
                    arr.append(x)
                    cap.release()
                index += 1
                i -= 1
            return arr

    def add_camera_field(self):

        def departments_ID():
    
            sql = 'SELECT * FROM department'
            self.mycursor.execute(sql)
            departments = self.mycursor.fetchall()

            department_id = []
            department_name = []
            spinvals_department = []
            for department in departments:
                department_id.append(department[0])
                name_d = department[1]
                department_name.append(name_d)

            for x in range(len(department_id)):
                # line_d = ' | '.join([str(department_id[x]),department_name[x]])
                spinvals_department.append(str(department_id[x]))
            return spinvals_department

        target = self.ids.ops_fields_c
        target.clear_widgets()
        crud_dep = Spinner(text='Department ID',values=departments_ID())
        crud_cam = Spinner(text='Camera ID',values=self.returnCameraIndexes())
        crud_submit = Button(text='Add',size_hint_x=None,width=100
        ,on_release=lambda x:self.add_camera(crud_cam.text,crud_dep.text))

        target.add_widget(crud_cam)
        target.add_widget(crud_dep)
        target.add_widget(crud_submit)

    def add_camera(self,camera,dep):

        if camera == '' or dep == '':
            self.notify.add_widget(Label(text='[color=#FF0000][b]All Fields Required[/b][/color]',markup=True))
            self.notify.open()
            Clock.schedule_once(self.killwsitch,1)
        else:
            sql = 'INSERT INTO cameras(camera_id,deparment_id,date_added) Values(%s,%s,%s)'
            values = [camera,dep,datetime.now()]
            self.mycursor.execute(sql,values)
            self.mydb.commit()
            content = self.ids.scrn_camera_contents
            content.clear_widgets()

            cameras = self.get_camera()
            camerastable = DataTable(table=cameras)
            content.add_widget(camerastable)

    def get_camera(self):
        mydb = mysql.connector.connect(
            host = 'localhost',
            user='root',
            passwd='',
            database='test'
        )
        mycursor = mydb.cursor()

        _cameras= OrderedDict()
        
        _cameras['Camera ID'] = {}
        _cameras['Department ID'] = {}
        _cameras['Date Added'] = {}

        camera_id = []
        department_id = []
        date_added = []

        sql = 'SELECT * FROM cameras'
        mycursor.execute(sql)
        cameras = mycursor.fetchall()

        for camera in cameras:
            camera_id.append(camera[0])
            department_id.append(camera[1])
            date_added.append(camera[2])

        users_length = len(camera_id)
        idx = 0 
        while idx < users_length:
            _cameras['Camera ID'][idx] = camera_id[idx]
            _cameras['Department ID'][idx] = department_id[idx]
            _cameras['Date Added'][idx] = date_added[idx]
            idx += 1
        return _cameras
    
    #===========================User Functions===============================

    def add_user_field(self):
        target = self.ids.ops_fields
        target.clear_widgets()
        crud_first = TextInput(hint_text='First Name')
        crud_last = TextInput(hint_text='Last Name')
        crud_user = TextInput(hint_text='User Name')
        crud_pwd = TextInput(hint_text='Password')
        crud_des = Spinner(text='Role',values=['Manager','Administrator'])
        crud_submit = Button(text='Add',size_hint_x=None,width=100,on_release=lambda x:
        self.add_user(crud_first.text,crud_last.text,crud_user.text,
        crud_pwd.text,crud_des.text))

        target.add_widget(crud_first)
        target.add_widget(crud_last)
        target.add_widget(crud_user)
        target.add_widget(crud_pwd)
        target.add_widget(crud_des)
        target.add_widget(crud_submit)

    def add_user(self,first,last,user,pwd,des):

        if first == '' or last == '' or user == '' or pwd == '' :
            self.notify.add_widget(Label(text='[color=#FF0000][b]All Fields Required[/b][/color]',markup=True))
            self.notify.open()
            Clock.schedule_once(self.killwsitch,1)
        else:
            sql = 'INSERT INTO users(first_name,last_name,user_names,passwords,designations,date) Values(%s,%s,%s,%s,%s,%s)'
            values = [first,last,user,pwd,des,datetime.now()]
            self.mycursor.execute(sql,values)
            self.mydb.commit()
            content = self.ids.scrn_contents
            content.clear_widgets()

            users = self.get_users()
            userstable = DataTable(table=users)
            content.add_widget(userstable)

    def update_user_field(self):
        target = self.ids.ops_fields
        target.clear_widgets()
        crud_first = TextInput(hint_text='First Name')
        crud_last = TextInput(hint_text='Last Name')
        crud_user = TextInput(hint_text='User Name')
        crud_pwd = TextInput(hint_text='Password')
        crud_des = Spinner(text='Operator',values=['Operator','Administrator'])
        crud_submit = Button(text='Update',size_hint_x=None,width=100,on_release=lambda x:
        self.update_user(crud_first.text,crud_last.text,crud_user.text,
        crud_pwd.text,crud_des.text))

        target.add_widget(crud_first)
        target.add_widget(crud_last)
        target.add_widget(crud_user)
        target.add_widget(crud_pwd)
        target.add_widget(crud_des)
        target.add_widget(crud_submit)

    def update_user(self,first,last,user,pwd,des):

        if first == '' or last == '' or user == '' or pwd == '' :
            self.notify.add_widget(Label(text='[color=#FF0000][b]All Fields Required[/b][/color]',markup=True))
            self.notify.open()
            Clock.schedule_once(self.killwsitch,1)
        else:
            sql = 'UPDATE users SET first_name = %s,last_name = %s,user_names = %s,passwords = %s,designations = %s WHERE user_names=%s'
            values = [first,last,user,pwd,des,user]
            self.mycursor.execute(sql,values)
            self.mydb.commit()

            content = self.ids.scrn_contents
            content.clear_widgets()

            users = self.get_users()
            userstable = DataTable(table=users)
            content.add_widget(userstable)

    def remove_user_field(self):
        target = self.ids.ops_fields
        target.clear_widgets()
        crud_user = TextInput(hint_text='User Name')
        crud_submit = Button(text='Remove',size_hint_x=None,width=100,on_release=lambda x:
        self.remove_user(crud_user.text))

        target.add_widget(crud_user)
        target.add_widget(crud_submit)

    def remove_user(self,user):

        if user == '':
            self.notify.add_widget(Label(text='[color=#FF0000][b]All Fields Required[/b][/color]',markup=True))
            self.notify.open()
            Clock.schedule_once(self.killwsitch,1)
        else:
            sql = 'DELETE FROM users WHERE user_names = %s'
            values = [user]
            self.mycursor.execute(sql,values)
            self.mydb.commit()
            content = self.ids.scrn_contents
            content.clear_widgets()

            users = self.get_users()
            userstable = DataTable(table=users)
            content.add_widget(userstable)

    def get_users(self):
        mydb = mysql.connector.connect(
            host = 'localhost',
            user='root',
            passwd='',
            database='test'
        )
        mycursor = mydb.cursor()

        _users= OrderedDict()
        
        _users['First Names'] = {}
        _users['Last Names'] = {}
        _users['User Names'] = {}
        _users['Passwords'] = {}
        _users['Designations'] = {}
        _users['Date Added'] = {}

        first_names = []
        last_names = []
        user_names = []
        passwords = []
        designations = []
        date_added = []

        sql = 'SELECT * FROM users'
        mycursor.execute(sql)
        users = mycursor.fetchall()

        for user in users:
            first_names.append(user[0])
            last_names.append(user[1])
            user_names.append(user[2])
            pwd = user[3]
            if len(pwd)>10:
                pwd = pwd[:10] + '...'
            passwords.append(pwd)
            designations.append(user[4])
            date_added.append(user[5])

        users_length = len(first_names)
        idx = 0 
        while idx < users_length:
            _users['First Names'][idx] = first_names[idx]
            _users['Last Names'][idx] = last_names[idx]
            _users['User Names'][idx] = user_names[idx]
            _users['Passwords'][idx] = passwords[idx]
            _users['Designations'][idx] = designations[idx]
            _users['Date Added'][idx] = date_added[idx]
            idx += 1
        return _users

    #===========================Employee Functions===============================

    def show_load(self):
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def load(self, path, filename):
        with open(os.path.join(path, filename[0])) as stream:
            pic_path = stream.name
            # print (stream.name)
            global file_path 
            file_path = pic_path
        self.dismiss_popup()

    def dismiss_popup(self):
        self._popup.dismiss()

    def add_employee_field(self):

        target = self.ids.ops_fields_emp
        target.clear_widgets()

        crud_cin = TextInput(hint_text='Cin Number')
        crud_name = TextInput(hint_text='First Name')
        crud_last = TextInput(hint_text='Last Name')
        crud_post = TextInput(hint_text="Employee's post")
        crud_depart = TextInput(hint_text='Department ID')
        crud_phone = TextInput(hint_text='Phone Number')
        crud_email = TextInput(hint_text='Email')
        crud_dob = TextInput(hint_text='Date Of Birth')

        crud_pic = Button(text='picture',size_hint_x=None,width=100,on_release=lambda x:self.show_load())


        crud_submit = Button(text='Add',size_hint_x=None,width=100,on_release=lambda x:
        self.add_employee(crud_cin.text,crud_name.text,crud_last.text,
        crud_post.text,crud_depart.text,crud_phone.text,crud_email.text,crud_dob.text,file_path))

        target.add_widget(crud_cin)
        target.add_widget(crud_name)
        target.add_widget(crud_last)
        target.add_widget(crud_post)
        target.add_widget(crud_depart)
        target.add_widget(crud_phone)
        target.add_widget(crud_email)
        target.add_widget(crud_dob)
        target.add_widget(crud_pic)
        target.add_widget(crud_submit)
        
    def add_employee(self,cin,name,last,post,depart_id,phone,email_emp,dob,pic):
        
        if cin == '' or name == '' or last == '' or post == '' or depart_id == '' or phone == '' or email_emp == '' or pic == '' :
            self.notify.add_widget(Label(text='[color=#FF0000][b]All Fields Required[/b][/color]',markup=True))
            self.notify.open()
            Clock.schedule_once(self.killwsitch,1)
        else:
            blob_value = open(pic, 'rb').read()

            sql = 'INSERT INTO employee(cin_number,first_name,last_name,post_employee,phone_number,email,date_of_birth,department_id,picture) Values(%s,%s,%s,%s,%s,%s,%s,%s,%s)'
            values = [cin,name,last,post,phone,email_emp,dob,depart_id,blob_value]
            self.mycursor.execute(sql,values)
            self.mydb.commit()
            content = self.ids.scrn_product_contents
            content.clear_widgets()
            global file_path
            file_path = ''

            prods = self.get_products()
            stocktable = DataTable(table=prods)
            content.add_widget(stocktable)

    def update_employee_field(self):
        target = self.ids.ops_fields_emp
        target.clear_widgets()

        crud_cin = TextInput(hint_text='Cin Number')
        crud_name = TextInput(hint_text='First Name')
        crud_last = TextInput(hint_text='Last Name')
        crud_post = TextInput(hint_text="Employee's post")
        crud_depart = TextInput(hint_text='Department ID')
        crud_phone = TextInput(hint_text='Phone Number')
        crud_email = TextInput(hint_text='Email')
        crud_dob = TextInput(hint_text='Date Of Birth')
        crud_pic = Button(text='picture',size_hint_x=None,width=100,on_release=lambda x:self.show_load())

        crud_submit = Button(text='Update',size_hint_x=None,width=100,on_release=lambda x:
        self.update_employee(crud_cin.text,crud_name.text,crud_last.text,
        crud_post.text,crud_depart.text,crud_phone.text,crud_email.text,crud_dob.text,file_path))

        target.add_widget(crud_cin)
        target.add_widget(crud_name)
        target.add_widget(crud_last)
        target.add_widget(crud_post)
        target.add_widget(crud_depart)
        target.add_widget(crud_phone)
        target.add_widget(crud_email)
        target.add_widget(crud_dob)
        target.add_widget(crud_pic)
        target.add_widget(crud_submit)

    def update_employee(self,cin,name,last,post,depart_id,phone,email_emp,dob,pic):
        
        if cin == '' or name == '' or last == '' or post == '' or depart_id == '' or phone == '' or email_emp == '' or dob == '' or pic == '':
            self.notify.add_widget(Label(text='[color=#FF0000][b]All Fields Required[/b][/color]',markup=True))
            self.notify.open()
            Clock.schedule_once(self.killwsitch,1)
        else:
            blob_value = open(pic, 'rb').read()
            sql = 'UPDATE employee SET cin_number = %s, first_name = %s, last_name = %s, post_employee = %s, phone_number = %s, email = %s, date_of_birth = %s, department_id = %s, picture = %s WHERE cin_number = %s'
            values = [cin,name,last,post,phone,email_emp,dob,depart_id,blob_value,cin]
            self.mycursor.execute(sql,values)
            self.mydb.commit()
            content = self.ids.scrn_product_contents
            content.clear_widgets()

            global file_path
            file_path = ''

            prods = self.get_products()
            stocktable = DataTable(table=prods)
            content.add_widget(stocktable)

    def remove_employee_field(self):
        target = self.ids.ops_fields_emp
        target.clear_widgets()

        crud_cin = TextInput(hint_text='CIN Number')
        crud_submit = Button(text='Remove',size_hint_x=None,width=100,on_release=lambda x:
        self.remove_employee(crud_cin.text))

        target.add_widget(crud_cin)
        target.add_widget(crud_submit)

    def remove_employee(self,code):
        
        if code == '':
            self.notify.add_widget(Label(text='[color=#FF0000][b]All Fields Required[/b][/color]',markup=True))
            self.notify.open()
            Clock.schedule_once(self.killwsitch,1)
        else:
            sql = 'DELETE FROM employee WHERE cin_number = %s'
            values = [code]
            self.mycursor.execute(sql,values)
            self.mydb.commit()
            content = self.ids.scrn_product_contents
            content.clear_widgets()

            prods = self.get_products()
            stocktable = DataTable(table=prods)
            content.add_widget(stocktable)

    def get_products(self):
        mydb = mysql.connector.connect(
            host = 'localhost',
            user='root',
            passwd='',
            database='test'
        )
        mycursor = mydb.cursor()
        _stocks= OrderedDict()

        _stocks['Cin Number'] = {}
        _stocks['First Name'] = {}
        _stocks['Last Name'] = {}
        _stocks['Post'] = {}
        _stocks['Phone Number'] = {}
        _stocks['Email'] = {}
        _stocks['Date Of Birth'] = {}
        # _stocks['Photo'] = {}
        
        cin_number = []
        first_name = []
        last_name = []
        post_employee = []
        phone_number = []
        email = []
        date_of_birth = []
        photo = []

        sql = 'SELECT * FROM employee '
        
        mycursor.execute(sql)
        employees = mycursor.fetchall()

        for employee_d in employees:
            cin_number.append(employee_d[1])
            first_name.append(employee_d[2])
            last_name.append(employee_d[3])
            post_employee.append(employee_d[4])
            phone_number.append(employee_d[5])
            email.append(employee_d[6])
            date_of_birth.append(employee_d[7])
            
            # photo.append(photo_emp)
        # photo_emp = open('sahnoun.jpg', 'wb').write(employees[1][9])
        
        employees_length = len(cin_number)
        idx = 0 
        while idx < employees_length:
            _stocks['Cin Number'][idx] = cin_number[idx]
            _stocks['First Name'][idx] = first_name[idx]
            _stocks['Last Name'][idx] = last_name[idx]
            _stocks['Post'][idx] = post_employee[idx]
            _stocks['Phone Number'][idx] = phone_number[idx]
            _stocks['Email'][idx] = email[idx]
            _stocks['Date Of Birth'][idx] = date_of_birth[idx]
            # _stocks['Photo'][idx] = photo[idx]
            
            idx += 1
        return _stocks

    def get_employees_department(self,dep_id):
        mydb = mysql.connector.connect(
            host = 'localhost',
            user='root',
            passwd='',
            database='test'
        )
        mycursor = mydb.cursor()
        _stocks= OrderedDict()

        _stocks['cin_number'] = {}
        _stocks['first_name'] = {}
        _stocks['last_name'] = {}
        _stocks['post_employee'] = {}
        _stocks['phone_number'] = {}
        _stocks['email'] = {}
        _stocks['date_of_birth'] = {}
        
        cin_number = []
        first_name = []
        last_name = []
        post_employee = []
        phone_number = []
        email = []
        date_of_birth = []

        sql = 'SELECT * FROM employee WHERE department_id = %s'
        value = [dep_id]
        mycursor.execute(sql,value)
        employees = mycursor.fetchall()

        for employee_d in employees:
            cin_number.append(employee_d[1])
            first_name.append(employee_d[2])
            last_name.append(employee_d[3])
            post_employee.append(employee_d[4])
            phone_number.append(employee_d[5])
            email.append(employee_d[6])
            date_of_birth.append(employee_d[7])
            

        employees_length = len(cin_number)
        idx = 0 
        while idx < employees_length:
            _stocks['cin_number'][idx] = cin_number[idx]
            _stocks['first_name'][idx] = first_name[idx]
            _stocks['last_name'][idx] = last_name[idx]
            _stocks['post_employee'][idx] = post_employee[idx]
            _stocks['phone_number'][idx] = phone_number[idx]
            _stocks['email'][idx] = email[idx]
            _stocks['date_of_birth'][idx] = date_of_birth[idx]
            
            idx += 1
        return _stocks

    #===========================================================================

class AdminApp(App):
    def build(self):
        return AdminWindow()

if __name__=='__main__':
    ad = AdminApp()
    ad.run()