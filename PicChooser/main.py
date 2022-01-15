from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty

from tkinter.filedialog import askopenfilename
from tkinter import Tk

class SampBoxLayout(BoxLayout):

    def get_image_one(self):
        '''This method is called by button FileChooser, it opens a FileChooser selects the desired image'''
        Tk().withdraw()
        img1 = askopenfilename(initialdir = "/",title = "Select file",filetypes = (("jpeg files","*.jpg"),("all files","*.*")))
        self.first_image.source = img1

    def check_for_image(self):
        '''This method is called by button TextIdentifier
           1. It needs to get the image selected by the above FileChooser
           2. The selected Image can be analysed further Ex: to check the if the selected image contains any text etc.
        '''
        pass

class SampleApp(App):
    def build(self):
        # Set the background color for the window
        Window.clearcolor = (1, 1, 1, 1)
        return SampBoxLayout()

sample_app = SampleApp()
sample_app.run()