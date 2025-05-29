'''
user_interface.py - User Interface for CreatConnect App

Manages UI layout, buttons, labels, and graph plotting.
'''

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.uix.image import Image
from kivy.clock import Clock
import time
from kivy.uix.anchorlayout import AnchorLayout
from kivy.core.window import Window
from kivy.app import App
from kivy.uix.widget import Widget

import sensor_input # Ensure this file exists and has read_sensor_data()
from graph import CreatinineGraph

Window.clearcolor = (1, 1, 1, 1) # Set window clear color to white

# StyleCard for a clean, rounded rectangular look
class StyleCard(BoxLayout):
    def __init__(self, **kwargs):
       super().__init__(orientation='vertical', padding=20, spacing=10, **kwargs)
       with self.canvas.before:
          Color(1,1,1,1) # White background for the card
          self.bg = RoundedRectangle(radius=[10], size=self.size, pos=self.pos)
       self.bind(pos=self.update_bg, size=self.update_bg)
    
    def update_bg(self, *args):
      self.bg.size = self.size
      self.bg.pos = self.pos

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
        text_size=(self.width - 40, None),
        height=140 if bold else 120
    )

    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', spacing=20, padding=20, **kwargs)
        
        # --- Top Header Section: Back Button, Logo, and Title ---
        header_container = BoxLayout(orientation='vertical', size_hint_y=None, height=130)

        # Top row for Back Button and Logo/Title
        top_row_header = BoxLayout(orientation='horizontal', size_hint_y=None, height=60)

        # Back Button (left side, anchored)
        back_button_anchor = AnchorLayout(anchor_x='left', anchor_y='center', size_hint=(None, 1), width=180)
        back_button = Button(text="[b]< Back to Menu[/b]", markup=True,
                             size_hint=(None, None), size=(240, 60), # Fixed size for button
                             background_normal='', background_color=(0.7, 0.7, 0.7, 1),
                             color=(0, 0, 0, 1), font_size='16sp')
        back_button.bind(on_release=self.go_back_to_menu)
        back_button_anchor.add_widget(back_button)
        top_row_header.add_widget(back_button_anchor)

        # Centered Logo (main title is below)
        logo_container = AnchorLayout(anchor_x="center", anchor_y="center", size_hint=(1, 1))
        logo = Image(source='FinalLogo.png', size_hint=(None, None), size=(200, 50)) # Adjusted size
        logo_container.add_widget(logo)
        top_row_header.add_widget(logo_container)

        header_container.add_widget(top_row_header)

        # Title label (below logo, centered)
        self.title_label = Label(text="[b]CreatConnect[/b]", markup=True,
                                 font_size='25sp', font_name='Roboto-Bold.ttf', size_hint=(1, None), height=40,
                                 halign='center', valign='middle', color=(0, 0, 0, 1))
        self.title_label.bind(size=self.title_label.setter('text_size'))
        header_container.add_widget(self.title_label)
        
        self.add_widget(header_container)
        # --- End Top Header Section ---


        # Status and Creatinine Readings (inside a StyleCard for visual grouping)
        status_creatinine_card = StyleCard(size_hint_y=None, height=120) 

        # Create a layout inside the card to manage status and creatinine labels
        status_creatinine_layout = BoxLayout(orientation='vertical', spacing=5)
        
        self.status_label = Label(text="[b][color=000000]Status:[/color][/b] [b][color=00aa00]Normal[/color][/b]",
            markup=True, font_size='18sp', size_hint_y=None, height=40)
        self.status_label.bind(size=self.status_label.setter('text_size'))
        status_creatinine_layout.add_widget(self.status_label)
   
        # FIX START: Initialize creatinine_label with placeholder text
        self.creatinine_label = Label(text="[b][color=000000]Creatinine: -- mg/dL[/color][/b]",
                              markup=True, font_size='18sp', size_hint_y=None, height=50) 
        # FIX END
        self.creatinine_label.bind(size=self.creatinine_label.setter('text_size'))
        status_creatinine_layout.add_widget(self.creatinine_label)
        
        status_creatinine_card.add_widget(status_creatinine_layout)
        self.add_widget(status_creatinine_card) # Add the card containing status and creatinine

        # Read Sensor Button
        self.read_button = Button(text="[b]Read Sensor[/b]",
             markup=True, size_hint=(1, None), height=50, background_normal='', background_color=(0.2, 0.6, 1, 1),
             color=(1, 1, 1, 1), font_size='18sp')
        self.read_button.bind(on_press=self.update_sensor_reading)
        self.add_widget(self.read_button)

        # Graph (inside its own StyleCard)
        graph_card = StyleCard(size_hint=(1, 1)) # Graph takes remaining vertical space
        self.graph = CreatinineGraph(size_hint=(1,1))
        graph_card.add_widget(self.graph)
        self.add_widget(graph_card)

        # Notes/Breakdown Label - Initialize here once
        self.breakdown_label = Label(text="[b]Breakdown:[/b]\n" # Initial static text
                                 "• Data not yet available.\n"
                                 "• Click 'Read Sensor' or wait for auto-update.", markup = True, color=(0,0,0,1), font_size='15sp', halign='left', valign='top',
                                 size_hint_y=None, height=120)
        self.breakdown_label.bind(size=self.breakdown_label.setter('text_size'))
        self.add_widget(self.breakdown_label)

        # Button to toggle trend line
        self.toggle_trend = Button(text="[b]Toggle Trend Line[/b]", markup=True, size_hint=(1, None), height=50, background_normal='',
                                   background_color=(0.2, 0.6, 1, 1), color=(1,1,1,1), font_size='16sp')
        self.toggle_trend.bind(on_press=self.toggle_trend_line)
        self.add_widget(self.toggle_trend)

        # --- CONSOLIDATED GRAPH DATA TRACKING INITIALIZATION ---
        self.readings = []
        self.timestamps = []
        self.start_time = time.time()
        # --- END CONSOLIDATED INITIALIZATION ---
        
        # Schedule the first update immediately, then every 30 seconds
     #   self.update_sensor_reading() # Call once at start to populate initial values
     #   Clock.schedule_interval(self.update_sensor_reading, 30) # Schedule for future updates

    def toggle_trend_line(self, instance):
        print("Trend line toggle clicked (feature not implemented yet)")

    def go_back_to_menu(self, instance):
        app = App.get_running_app()
        if app and hasattr(app, 'root') and hasattr(app.root, 'current'):
            app.root.current = 'menu_screen'
        else:
            print("Error: Could not access ScreenManager to switch screen.")

    def update_sensor_reading(self, instance=None):
        reading = 0.0
        print("Attempting to read sensor data...")
        try:
            reading = sensor_input.read_sensor_data()
            print(f"Successfully read sensor data: {reading}")
        except Exception as e:
            print(f"Error in sensor_input.read_sensor_data(): {e}. Using mock data.")
            import random
            reading = round(random.uniform(0.6, 1.3), 2)
            if random.random() < 0.05:
                reading = round(random.uniform(1.5, 2.5), 2)
            elif random.random() < 0.02:
                reading = round(random.uniform(0.3, 0.5), 2)

        # Update creatinine_label text here, now that 'reading' is defined
        self.creatinine_label.text = f"[b][color=000000]Creatinine: {reading} mg/dL[/b]"
        
        status = "Normal"
        color = "00aa00"
        
        # Build the breakdown message dynamically
        breakdown_text = "[b]Breakdown:[/b]\n" # Start with the bold "Breakdown:" header

        if reading > 1.3:
            status = "High"
            color = "ff9900"
            breakdown_text += "• Your creatinine levels are [color=ff9900]higher than normal[/color].\n" \
                                 "• Consult a healthcare professional for further evaluation."
            
        elif reading < 0.6:
            status = "Low"
            color = "cc0000"
            breakdown_text += "• Your creatinine levels are [color=cc0000]lower than normal[/color].\n" \
                                 "• Consult a healthcare professional for further evaluation."
        else: # Normal range
            breakdown_text += "• Your creatinine levels are within the normal range.\n" \
                                 "• No immediate abnormalities detected.\n" \
                                 "• Continue monitoring as advised by your doctor."

        self.status_label.text = f"[b][color=000000]Status:[/color][/b] [b][color={color}]{status}[/color][/b]"
        
        # Update the text of the existing breakdown_label
        self.breakdown_label.text = breakdown_text 

        current_time = round(time.time() - self.start_time, 2)
        self.readings.append(reading) # Ensure reading is added here
        self.timestamps.append(current_time)

        self.graph.update_graph(self.timestamps[-60:], self.readings[-60:])

        app = App.get_running_app()
        if hasattr(app, 'all_creatinine_readings'):
            print(self.readings)
            app.all_creatinine_readings = (self.readings)
            print(app.all_creatinine_readings)
        else:
            print("Warning: all_creatinine_readings not found on app instance.")
        sm = app.root
    def _trigger_menu_status_update(self, dt):
        # This method runs after the main Kivy build process
        app = App.get_running_app()
        sm = app.root # Now app.root should be the ScreenManager

        # Check if sm is not None before accessing its attributes
        if sm and sm.current == 'menu_screen':
            # Dynamically import menu_screen here, as it's only needed if this branch is taken
            import importlib
            menu_screen_module = importlib.import_module('menu_screen')
            
            # Ensure we get the correct MenuScreen instance
            # It's usually the first child of the Screen object named 'menu_screen'
            menu_screen_widget = sm.get_screen('menu_screen').children[0]
            
            if isinstance(menu_screen_widget, menu_screen_module.MenuScreen):
                menu_screen_widget.update_menu_status()
            else:
                print("Warning: Could not get MenuScreen instance to update status.")
        elif not sm:
            print("Debug: app.root (ScreenManager) is still None when _trigger_menu_status_update was called.")


    # def auto_update_sensor() --> Automatically fetches new data every 30 seconds
     #   Clock.schedule_interval(self.update_sensor_reading, 30)

    # def update_graph() --> Updates the graph with new readings





       

       


       