'''
main.py - Entry point for CreatConnect App
'''
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.core.text import LabelBase # Import LabelBase for font registration

from menu_screen import MenuScreen # Ensure this file and class exist
from user_interface import CreatConnectUI # The main sensor UI
from visual import VisualScreen # Ensure this file and class exist

import os

PAPER_COLOR = (0.95, 0.95, 0.9, 1) # Slightly off-white for paper
Window.clearcolor = PAPER_COLOR
current_dir = os.path.dirname(os.path.abspath(__file__))

# *** THIS LINE IS THE FIX ***
# Go up two directories ('..', '..'), then into the 'Roboto' folder
roboto_font_path = os.path.join(current_dir, '..', 'Roboto', 'static', 'Roboto-Regular.ttf')

LabelBase.register(name="Roboto", fn_regular=roboto_font_path)


class CreatConnectApp(App):
    def build(self):
        # Initialize the list to store all creatinine readings as an instance attribute.
        self.all_creatinine_readings = []

        # Create the screen manager
        sm = ScreenManager()

        # Create the Menu Screen (This will be the home screen)
        menu_screen = Screen(name='menu_screen')
        menu_screen.add_widget(MenuScreen()) # MenuScreen should be defined in menu_screen.py
        sm.add_widget(menu_screen)

        # Create the Sensor Graph Screen (your original UI)
        sensor_graph_screen = Screen(name='sensor_graph_screen')
        sensor_graph_screen.add_widget(CreatConnectUI())
        sm.add_widget(sensor_graph_screen)

        # Create the Visual Screen
        visual_screen = Screen(name='visual_screen')
        visual_screen.add_widget(VisualScreen()) # VisualScreen should be defined in visual.py
        sm.add_widget(visual_screen)

        # Set the initial screen to the menu
        sm.current = 'menu_screen'

        return sm

if __name__ == "__main__":
    CreatConnectApp().run()