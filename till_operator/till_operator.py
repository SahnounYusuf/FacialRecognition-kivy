from kivy.app import  App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

import mysql.connector
import re
from kivy.lang import Builder

Builder.load_file('till_operator/operator.kv')

class OperatorWindow(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mydb = mysql.connector.connect(
            host = 'localhost',
            user='root',
            passwd='',
            database='test'
        )
        self.mycursor = self.mydb.cursor()
        sql = 'SELECT * FROM employee'
        self.mycursor.execute(sql)
        self.stocks = self.mycursor.fetchall()

        self.cart = []
        self.qty = []
        self.total = 0.00

    def logout(self):
        self.parent.parent.current = 'scrn_si'
        
    def update_purchase(self):
        pcode = self.ids.code_inp.text 
        products_container = self.ids.products

        target_code = self.stocks
        if target_code == None:
            pass
        else:
            for stock in target_code:
                details = BoxLayout(size_hint_y=None,height=30,pos_hint={'top': 1})
                products_container.add_widget(details)

                code = Label(text=pcode,size_hint_x=.2,color=(.06,.45,.45,1))
                name = Label(text=stock[1],size_hint_x=.3,color=(.06,.45,.45,1))
                qty = Label(text='1',size_hint_x=.1,color=(.06,.45,.45,1))
                decs = Label(text='0.00',size_hint_x=.1,color=(.06,.45,.45,1))
                price = Label(text=stock[4],size_hint_x=.1,color=(.06,.45,.45,1))
                total = Label(text='0.00',size_hint_x=.2,color=(.06,.45,.45,1))
                details.add_widget(code)
                details.add_widget(name)
                details.add_widget(qty)
                details.add_widget(decs)
                details.add_widget(price)
                details.add_widget(total)

                #update preview 
                pname = name.text
                pprice = float(price.text)
                pqty = str(1)
                self.total += pprice
                puchase_total = '`\n\nTotal\t\t\t\t\t\t\t\t'+str(self.total)
                self.ids.cur_product.text = pname
                self.ids.cur_price.text = str(pprice)

                preview = self.ids.receipt_preview
                prev_text = preview.text 
                _prev = prev_text.find('`')
                if _prev > 0:
                    prev_text = prev_text[:_prev]

                ptarget = -1
                for i,c in enumerate(self.cart):
                    if c == pcode:
                        ptarget = i

                if ptarget >=0:
                    pqty = self.qty[ptarget]+1
                    self.qty[ptarget] = pqty
                    expr = '%s\t\tx\d\t'%(pname)
                    rexpr = pname+'\t\tx'+str(pqty)+'\t'
                    nu_text = re.sub(expr,rexpr,prev_text)
                    preview.text = nu_text + puchase_total
                else:
                    self.cart.append(pcode)
                    self.qty.append(1)
                    nu_preview = '\n'.join([prev_text,pname+'\t\tx'+str(pqty)+'\t\t'+str(pprice)
                    ,puchase_total])
                    preview.text = nu_preview
                self.ids.disc_inp.text = '0;00'
                self.ids.disc_prec_inp.text = '0'
                self.ids.qty_inp.text = str(pqty)
                self.ids.price_inp.text = str(pprice)
                self.ids.vat_inp.text = '15%'
                self.ids.total_inp.text = str(pprice)


class OperatorApp(App):
    def build(self):
        return OperatorWindow()

if __name__=="__main__":
    oa = OperatorApp()
    oa.run()