'''
user_interface.py - User Interface for CreatConnect App

Manages UI layout, buttons, labels, and graph plotting.
'''

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.graph import Graph
# from kivy.clock import Clock
# from sensor_input import read_sensor_data 
# from data_storage import DataManager 

class CreateConnectUI(BoxLayout):
    def __init__(self):
       '''
       Initizalize User Interface
       ''' 
       super().__init__(orientation='vertical', padding=20, spacing=10)

       # Label for creatinine level
       self.creatinine_label = Label(text="Creatinine: -- mg/dL", font_size='20sp')

       # Button to read sensor data 
       self.read_button = Button(text="Read Sensor", size_hint=(1, 0.2))
       self.read_button.bind(on_press=self.update_sensor_reading)
       
       # Graph for data 
       self.graph = Graph()
       
       # Widgets
       self.add_widget(self.creatinine_label)
       self.add_widget(self.read_button)
       self.add_widget(self.graph)

       # Data Storage Manager
       # self.data_manager = DataManager()

       # Schedule auto-update every 30 seconds

    # def update_sensor_reading() --> Fetches a new sensor reading and updates the UI

    # def auto_update_sensor() --> Automatically fetches new data every 30 seconds

    # def update_graph() --> Updates the graph with new readings





       

       


       




