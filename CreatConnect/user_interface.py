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
from kivy.uix.image import Image
from graph import CreatinineGraph
from kivy.clock import Clock
import time
from kivy.uix.anchorlayout import AnchorLayout
from kivy.graphics import RoundedRectangle
from kivy.core.window import Window
# from history import DataManager
# from graph import CreatinineGraph
# from kivy.clock import Clock
# from data_storage import DataManager 
Window.clearcolor = (1, 1, 1, 1) 

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
      # Title: CreatConnect by SensTech
        title_section = BoxLayout(orientation='vertical', size_hint=(1, None), height=130, padding=[10, 10], spacing=5)
        self.title_label = Label(text="[b]CreatConnect[/b] ",markup=True,
                           font_size='30sp', font_name='Exo2-Bold.otf', size_hint=(1, None), width=300, halign='center', valign= 'middle', color=(0, 0, 0, 1))
        self.title_label.bind(size=self.title_label.setter('text_size'))

        title_section.add_widget(self.title_label)
        self.add_widget(title_section)
        # HEADER
        self.status_label = Label(text="[b][color=000000]Status:[/color][/b] [b][color=00aa00]Normal[/color][/b]",
            markup=True, font_size='18sp', size_hint=(1, None),height=30)
   

        # Creatinine Reading
        self.creatinine_label = Label( text="[b][color=000000]Creatinine: -- mg/dL[/color][/b]",
         markup=True, font_size='22sp',size_hint=(1, None),height=40)

        # Read Sensor Button
        self.read_button = Button(text="[b]Read Sensor[/b]",
         markup=True, size_hint=(1, None), height=50, background_normal='', background_color=(0.2, 0.6, 1, 1),
         color=(1, 1, 1, 1),font_size='18sp')
        self.add_widget(self.read_button)

         # Graph
        self.graph = CreatinineGraph(size_hint=(1,1))

        self.card = StyleCard(size_hint=(1, 1))
        self.card.add_widget(self.status_label)
        self.card.add_widget(self.creatinine_label)
        self.card.add_widget(self.graph)
        self.add_widget(self.card)

        # Notes and Trendline Toggle
        breakdown_label = Label(text="[b]Breakdown:[/b]\n"
         "• Your creatinine levels are within the normal range.\n"
         "• No abnormalities detected.\n"
         "• Last 7 days trending normal.", markup = True, color=(0,0,0,1), font_size='15sp', halign='left', valign='top',
        size_hint=(1,None), height=120)
        self.add_widget(breakdown_label)

        # Button to toggle trend line
        self.toggle_trend = Button(text="Toggle Trend Line", size_hint=(1, None), height=50, background_normal='',
                                   background_color=(0.2, 0.6, 1, 1), color=(1,1,1,1), font_size='16sp')
        self.toggle_trend.bind(on_press=self.toggle_trend_line)
        self.add_widget(self.toggle_trend)

        # Sensor Read Button
        self.read_button.bind(on_press=self.update_sensor_reading)

        # For graph data tracking
        self.time_elapsed = []
        self.readings = []
        self.start_time = time.time()

        # Auto-update sensor every 30 seconds
        Clock.schedule_interval(self.update_sensor_reading, 30)

        # Senstech Logo
        logo_container = AnchorLayout(anchor_x="left", anchor_y="top", size_hint=(1,None), height=100)
        logo = Image(source='FinalLogo.png', size_hint=(None,None), size=(220,80))  # Removed allow_stretch / keep_ratio — deprecated
        logo_container.add_widget(logo)
        self.add_widget(logo_container, index=0)

        self.readings = []
        self.timestamps = []
        self.start_time = time.time()

        
        # History data
        # self.data = DataManager()
    def toggle_trend_line(self, instance):
      print("Trend line toggle clicked (feature not implemented yet)")

    # def update_sensor_reading() --> Fetches a new sensor reading and updates the UI
    def update_sensor_reading(self, instance):
      reading = sensor_input.read_sensor_data()
      self.creatinine_label.text = f"Creatinine: {reading} mg/dL"

      current_time = round(time.time() - self.start_time,2)
      self.readings.append(reading)
      self.timestamps.append(current_time)

      self.graph.update_graph(self.timestamps[-60:], self.readings[-60:])  # last 60 points


      # Check range for status
      status = "Normal"
      color = "00aa00"  

      self.status_label.text = f"[b][color=000000]Status:[/color][/b] [b][color={color}]{status}[/color][/b]"

class StyleCard(BoxLayout):
    def __init__(self, **kwargs):
       super().__init__(orientation='vertical', padding=20, spacing=10, **kwargs)
       with self.canvas.before:
          Color(1,1,1,1)
          self.bg = RoundedRectangle(radius=[10], size=self.size, pos=self.pos)
       self.bind(pos=self.update_bg, size=self.update_bg)
    
    def update_bg(self, *args):
      self.bg.size = self.size
      self.bg.pos = self.pos


    # def auto_update_sensor() --> Automatically fetches new data every 30 seconds

    # def update_graph() --> Updates the graph with new readings





       

       


       




