'''
user_interface.py - User Interface for CreatConnect App

Manages UI layout, buttons, labels, and graph plotting.
'''

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy_garden.graph import Graph, LinePlot
import sensor_input
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, Rectangle
# from history import DataManager
# from graph import CreatinineGraph
# from kivy.clock import Clock
# from data_storage import DataManager 

class CreatConnectUI(BoxLayout):
    def make_wrapped_label(self, text, bold=False):
     return Label(
        text=text,
        markup=True,
        font_size='15sp',
        size_hint_y=None,
        halign='left',
        valign='top',
        color=(0.1, 0.1, 0.1, 1),
        text_size=(self.width - 40, None),  # Will auto-adjust as layout resizes
        height=140 if bold else 120
    )
    def __init__(self):
        super().__init__(orientation='vertical', spacing=20, padding=20)
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0.95, 0.95, 0.95, 1)  # Light background
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_bg, pos=self.update_bg)

        # HEADER
        self.status_label = Label(text="[b][color=000000]Status:[/color][/b] [b][color=00aa00]Normal[/color][/b]",
            markup=True, font_size='18sp', size_hint=(1, None),height=30)
        
        self.add_widget(self.status_label)

        # Creatinine Reading
        self.creatinine_label = Label( text="[b][color=000000]Creatinine: -- mg/dL[/color][/b]",
         markup=True, font_size='22sp',size_hint=(1, None),height=40)

        self.add_widget(self.creatinine_label)

        # Graph
        # self.graph = CreatinineGraph()
        # self.add_widget(self.graph)

        # Read Sensor Button
        self.read_button = Button(text="[b]Read Sensor[/b]",
         markup=True, size_hint=(1, None), height=50, background_normal='', background_color=(0.2, 0.6, 1, 1),
         color=(1, 1, 1, 1),font_size='18sp')
        self.add_widget(self.read_button)

        # History data
        # self.data = DataManager()

    # def update_sensor_reading() --> Fetches a new sensor reading and updates the UI
    def update_sensor_reading(self, instance):
      reading = sensor_input.read_sensor_data()
      self.data.store_reading(reading)
      self.creatinine_label.text = f"Creatinine: {reading} mg/dL"

      # Check range for status
      status = "Normal"
      color = "00aa00"
      if reading < 0.6:
         status = "Low"
         color = "ffaa00"
      elif reading > 1.1:
         status = "High"
         color = "ff0000"

      self.status_label.text = f"Status: [color={color}]{status}[/color]"

      # Update graph
      x, y = self.data.get_graph_data()
      self.graph.update_graph(x, y)

    def update_bg(self, *args):
      self.bg_rect.size = self.size
      self.bg_rect.pos = self.pos


    # def auto_update_sensor() --> Automatically fetches new data every 30 seconds

    # def update_graph() --> Updates the graph with new readings





       

       


       




