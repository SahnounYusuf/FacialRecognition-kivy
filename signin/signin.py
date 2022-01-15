from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder

import mysql.connector
import hashlib

Builder.load_file('signin/signin.kv')

def logintodb(user, passw):
     
        # If paswword is enetered by the 
        # user
        mydb = mysql.connector.connect(
            host = 'localhost',
            user='root',
            passwd='',
            database='test'
        )
        mycursor = mydb.cursor()
            
        # A Table in the database
        sql = 'select designations from users where user_names = %s and passwords = %s'
        values = [user,passw]

        print (user)
        print (passw)
        
        try:
            mycursor.execute(sql,values)
            myresult = mycursor.fetchall()
            
            # Printing the result of the
            # query
            for x in myresult:
                user_role = x[0]
                print(x)
            print("Query Excecuted successfully")
            return user_role
        except:
            mydb.rollback()
            print("Error occured")
            return myresult
        
class SigninWindow(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def validate_user(self):

        user = self.ids.username_field
        pwd = self.ids.pwd_field
        info = self.ids.info

        uname = user.text
        passw = pwd.text

        # passw = hashlib.sha256(passw.encode()).hexdigest()
        print(logintodb(uname,passw))
        user_account = logintodb(uname,passw)
        user.text = ''
        pwd.text = ''

        if uname == '' or passw == '':
            info.text = '[color=#FF0000]username and/ or password required[/color]'
        else:
            if user_account == []:
                info.text = '[color=#FF0000]Invalid Username and/or Password[/color]'
            else:
                des = user_account
                info.text = '[color=#00FF00]Logged In successfully!!![/color]'
                info.text = ''
                self.parent.parent.parent\
                            .ids.scrn_op.children[0]\
                                .ids.loggedin_user.text = uname
                if des == 'Administrator':
                    self.parent.parent.current = 'scrn_admin'
                else:
                    self.parent.parent.current = 'scrn_op'

class SigninApp(App):
    def build(self):
        return SigninWindow()

if __name__=="__main__":
    sa = SigninApp()
    sa.run()