'''
user_interface.py - User Interface for CreatConnect App

Manages UI layout, buttons, labels, and graph plotting.
'''

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, Rectangle, Line, RoundedRectangle, Mesh
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.clock import Clock
import time
from kivy.uix.anchorlayout import AnchorLayout
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.properties import ListProperty, NumericProperty
from kivy.uix.screenmanager import Screen
import numpy as np 
from graph import CreatinineGraph # Import CreatinineGraph
import sensor_input # Assuming this file exists and has read_sensor_data()

# --- Configuration for Sketch Style ---
SKETCH_LINE_WIDTH = 1.5 # Thicker lines for sketch
SKETCH_COLOR = (0.2, 0.2, 0.2, 1) # Dark grey for "pencil" lines
PAPER_COLOR = (0.95, 0.95, 0.9, 1) # Slightly off-white for paper
HIGHLIGHT_COLOR = (0.5, 0.7, 0.9, 1) # A muted blue for active elements

# Set window clear color to simulate paper
Window.clearcolor = PAPER_COLOR

HANDWRITTEN_FONT = 'Roboto'

def rgb_to_hex(rgb_tuple):
    return f"{int(rgb_tuple[0]*255):02x}{int(rgb_tuple[1]*255):02x}{int(rgb_tuple[2]*255):02x}"

SKETCH_COLOR_HEX = rgb_to_hex(SKETCH_COLOR)
HIGHLIGHT_COLOR_HEX = rgb_to_hex(HIGHLIGHT_COLOR)

# --- Custom SketchButton Widget ---

class VisualScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # ... rest of your VisualScreen class code    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = '' # Remove default background
        self.background_down = ''
        self.color = SKETCH_COLOR # Set text color

        with self.canvas.before:
            self.sketch_color = Color(*SKETCH_COLOR)
            self.sketch_rect = Rectangle(pos=self.pos, size=self.size) # For potential background fill
            self.sketch_border_lines = Line(points=[], width=SKETCH_LINE_WIDTH)

        self.bind(pos=self.update_graphics, size=self.update_graphics)

    def update_graphics(self, *args):
        self.sketch_rect.pos = self.pos
        self.sketch_rect.size = self.size

        # Simulate rough rectangle lines
        x, y = self.pos
        w, h = self.size
        
        # Add some random jitter to lines for a hand-drawn look
        jitter_amount = dp(2) # Jitter amount
        
        points = [
            x + (np.random.rand() * jitter_amount - jitter_amount/2), y + (np.random.rand() * jitter_amount - jitter_amount/2), # Bottom-left
            x + w + (np.random.rand() * jitter_amount - jitter_amount/2), y + (np.random.rand() * jitter_amount - jitter_amount/2), # Bottom-right
            x + w + (np.random.rand() * jitter_amount - jitter_amount/2), y + h + (np.random.rand() * jitter_amount - jitter_amount/2), # Top-right
            x + (np.random.rand() * jitter_amount - jitter_amount/2), y + h + (np.random.rand() * jitter_amount - jitter_amount/2), # Top-left
            x + (np.random.rand() * jitter_amount - jitter_amount/2), y + (np.random.rand() * jitter_amount - jitter_amount/2) # Close loop
        ]
        self.sketch_border_lines.points = points
        
        # Change color on press
        if self.state == 'down':
            self.sketch_color.rgb = HIGHLIGHT_COLOR # Use a different color when pressed
        else:
            self.sketch_color.rgb = SKETCH_COLOR

# --- Custom StyleCard for Sketch Look ---
class StyleCard(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=dp(20), spacing=dp(10), **kwargs)
        with self.canvas.before:
            Color(*PAPER_COLOR)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
            
            Color(*SKETCH_COLOR)
            self.sketch_border = Line(points=[], width=SKETCH_LINE_WIDTH)
        
        self.bind(pos=self.update_graphics, size=self.update_graphics)
    
    def update_graphics(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

        x, y = self.pos
        w, h = self.size
        
        jitter_amount = dp(3) 
        points = [
            x + (np.random.rand() * jitter_amount - jitter_amount/2), y + (np.random.rand() * jitter_amount - jitter_amount/2), # Bottom-left
            x + w + (np.random.rand() * jitter_amount - jitter_amount/2), y + (np.random.rand() * jitter_amount - jitter_amount/2), # Bottom-right
            x + w + (np.random.rand() * jitter_amount - jitter_amount/2), y + h + (np.random.rand() * jitter_amount - jitter_amount/2), # Top-right
            x + (np.random.rand() * jitter_amount - jitter_amount/2), y + h + (np.random.rand() * jitter_amount - jitter_amount/2), # Top-left
            x + (np.random.rand() * jitter_amount - jitter_amount/2), y + (np.random.rand() * jitter_amount - jitter_amount/2) # Close loop
        ]
        self.sketch_border.points = points

# --- Status Color Bar (Sketch-style) ---
class StatusColorBar(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            # Top: Red (abnormal high)
            Color(0.8, 0.2, 0.2, 1) # Muted red
            self.red_rect = Rectangle(pos=(self.x, self.top - dp(60)), size=(dp(50), dp(60)))
            # Middle: Green (normal)
            Color(0.2, 0.7, 0.2, 1) # Muted green
            self.green_rect = Rectangle(pos=(self.x, self.top - dp(120)), size=(dp(50), dp(60)))
            # Bottom: Orange (abnormal low)
            Color(0.9, 0.5, 0.1, 1) # Muted orange
            self.orange_rect = Rectangle(pos=(self.x, self.top - dp(180)), size=(dp(50), dp(60)))
            
            Color(*SKETCH_COLOR) # Sketch border for the whole bar
            self.bar_border = Line(points=[], width=SKETCH_LINE_WIDTH)

        self.bind(pos=self.update_graphics, size=self.update_graphics)

    def update_graphics(self, *args):
        # Update positions of rectangles
        self.red_rect.pos = (self.x, self.top - dp(60))
        self.red_rect.size = (self.width, dp(60)) # Use self.width for consistent sizing
        
        self.green_rect.pos = (self.x, self.top - dp(120))
        self.green_rect.size = (self.width, dp(60))
        
        self.orange_rect.pos = (self.x, self.top - dp(180))
        self.orange_rect.size = (self.width, dp(60))

        # Draw a single rough border around the entire bar
        x, y = self.pos
        w, h = self.size
        
        jitter_amount = dp(2) # Jitter for the bar border
        points = [
            x + (np.random.rand() * jitter_amount - jitter_amount/2), y + (np.random.rand() * jitter_amount - jitter_amount/2), # Bottom-left
            x + w + (np.random.rand() * jitter_amount - jitter_amount/2), y + (np.random.rand() * jitter_amount - jitter_amount/2), # Bottom-right
            x + w + (np.random.rand() * jitter_amount - jitter_amount/2), y + h + (np.random.rand() * jitter_amount - jitter_amount/2), # Top-right
            x + (np.random.rand() * jitter_amount - jitter_amount/2), y + h + (np.random.rand() * jitter_amount - jitter_amount/2), # Top-left
            x + (np.random.rand() * jitter_amount - jitter_amount/2), y + (np.random.rand() * jitter_amount - jitter_amount/2) # Close loop
        ]
        self.bar_border.points = points

# --- Menu Popup (Sketch-style) ---
class MenuPopup(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "Menu"
        self.title_font = HANDWRITTEN_FONT
        self.title_color = SKETCH_COLOR

        layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))
        options = ["Call Doctor", "History Log", "Detailed History Graph", "Sensor Graph", "Health Info", "View Visuals"]
        for opt in options:
            btn = SketchButton(text=opt, size_hint_y=None, height=dp(40),
                               font_name=HANDWRITTEN_FONT, font_size='16sp')
            if opt == "View Visuals":
                btn.bind(on_release=self.switch_to_visual_screen)
            layout.add_widget(btn)
        self.content = layout
        self.size_hint = (None, None)
        self.size = (dp(300), dp(400))
        
        # Override Popup's background and border for sketch look
        self.background_color = (0,0,0,0) # Make it transparent so we can draw our own
        with self.canvas.before:
            Color(*PAPER_COLOR)
            self.popup_bg_rect = Rectangle(pos=self.pos, size=self.size)
            Color(*SKETCH_COLOR)
            self.popup_border = Line(points=[], width=SKETCH_LINE_WIDTH)
        self.bind(pos=self.update_popup_graphics, size=self.update_popup_graphics)

    def update_popup_graphics(self, *args):
        self.popup_bg_rect.pos = self.pos
        self.popup_bg_rect.size = self.size
        
        x, y = self.pos
        w, h = self.size
        jitter_amount = dp(3)
        points = [
            x + (np.random.rand() * jitter_amount - jitter_amount/2), y + (np.random.rand() * jitter_amount - jitter_amount/2),
            x + w + (np.random.rand() * jitter_amount - jitter_amount/2), y + (np.random.rand() * jitter_amount - jitter_amount/2),
            x + w + (np.random.rand() * jitter_amount - jitter_amount/2), y + h + (np.random.rand() * jitter_amount - jitter_amount/2),
            x + (np.random.rand() * jitter_amount - jitter_amount/2), y + h + (np.random.rand() * jitter_amount - jitter_amount/2),
            x + (np.random.rand() * jitter_amount - jitter_amount/2), y + (np.random.rand() * jitter_amount - jitter_amount/2)
        ]
        self.popup_border.points = points

    def switch_to_visual_screen(self, instance):
        self.dismiss() # Close the popup
        # Access the ScreenManager which is the root of the app
        from kivy.app import App
        app = App.get_running_app()
        if app and hasattr(app, 'root') and hasattr(app.root, 'current'):
            app.root.current = 'visual_screen'
        else:
            print("Error: Could not access ScreenManager to switch screen.")


class CreatConnectUI(BoxLayout):
    def make_wrapped_label(self, text, bold=False):
        # Adjusted for sketch style font and color
        return Label(
            text=text,
            markup=True,
            font_size='15sp',
            font_name=HANDWRITTEN_FONT, # Use custom font
            size_hint_y=None,
            halign='left',
            valign='top',
            color=SKETCH_COLOR, # Use sketch color for text
            text_size=(self.width - dp(40), None),
            height=dp(140) if bold else dp(120)
        )

    def __init__(self):
        super().__init__(orientation='vertical', spacing=dp(15), padding=dp(15)) # Reduced spacing slightly

        # Title: CreatConnect by SensTech
        title_section = BoxLayout(orientation='horizontal', size_hint=(1, None), height=dp(100), padding=[dp(10), dp(0)], spacing=dp(5)) # Horizontal for logo and title
        logo_container = AnchorLayout(anchor_x="left", anchor_y="center", size_hint=(None, 1), width=dp(220))
        logo = Image(source='FinalLogo.png', size_hint=(None,None), size=(dp(220),dp(80))) # Replace with your logo
        logo_container.add_widget(logo)
        title_section.add_widget(logo_container)
        self.title_label = Label(text="CreatConnect", font_size='35sp', font_name=HANDWRITTEN_FONT,
                                   halign='left', valign='middle', color=SKETCH_COLOR, size_hint=(1, 1))
        self.title_label.bind(size=self.title_label.setter('text_size'))
        title_section.add_widget(self.title_label)
        menu_btn_container = AnchorLayout(anchor_x='right', anchor_y='center', size_hint=(None, 1), width=dp(60))
        menu_btn = SketchButton(text="☰", size_hint=(1, 1), font_size='25sp', font_name=HANDWRITTEN_FONT)
        menu_btn.bind(on_release=lambda x: MenuPopup().open())
        menu_btn_container.add_widget(menu_btn)
        title_section.add_widget(menu_btn_container)
        self.add_widget(title_section)

        # Header (Status and Creatinine)
        header_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(60), spacing=dp(5))
        self.status_label = Label(text=f"[b][color={SKETCH_COLOR_HEX}]Status:[/color][/b] [b][color=00aa00]Normal[/color][/b]", markup=True, font_size='18sp', font_name=HANDWRITTEN_FONT, size_hint=(1, None), height=dp(30))
        self.status_label.bind(size=self.status_label.setter('text_size'))
        header_layout.add_widget(self.status_label)
        self.creatinine_label = Label(text=f"[b][color={SKETCH_COLOR_HEX}]Creatinine:[/color][/b] -- mg/dL", markup=True, font_size='22sp', font_name=HANDWRITTEN_FONT, size_hint=(1, None), height=dp(30))
        self.creatinine_label.bind(size=self.creatinine_label.setter('text_size'))
        header_layout.add_widget(self.creatinine_label)
        self.add_widget(header_layout)

        # Read Sensor Button
        self.read_button = SketchButton(text="[b]Read Sensor[/b]", markup=True, size_hint=(1, None), height=dp(50), font_size='18sp', font_name=HANDWRITTEN_FONT)
        self.add_widget(self.read_button)
        self.read_button.bind(on_press=self.update_sensor_reading)

        # Graph and Status Bar Layout
        graph_and_bar_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.6)) # Adjusted size_hint for graph area
        self.graph = CreatinineGraph(size_hint=(0.8, 1)) # Graph takes 80% of the horizontal space
        graph_and_bar_layout.add_widget(self.graph)
        status_bar_container = AnchorLayout(anchor_x='center', anchor_y='center', size_hint=(0.2, 1)) # Status bar takes 20%
        self.status_bar = StatusColorBar(size_hint=(None, None), size=(dp(50), dp(180)))
        status_bar_container.add_widget(self.status_bar)
        graph_and_bar_layout.add_widget(status_bar_container)
        self.add_widget(graph_and_bar_layout)

        # Breakdown Label
        breakdown_text = "[b]Breakdown:[/b]\n" \
                         "• Your creatinine levels are within the normal range.\n" \
                         "• No abnormalities detected.\n" \
                         "• Last 7 days trending normal."
        breakdown_label = Label(text=f"[color={SKETCH_COLOR_HEX}]{breakdown_text}[/color]", markup=True, font_size='15sp', font_name=HANDWRITTEN_FONT, halign='left', valign='top', size_hint_y=None, height=dp(100))
        breakdown_label.bind(size=breakdown_label.setter('text_size'))
        self.add_widget(breakdown_label)

        # Action Buttons (Toggle and Share)
        actions_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=dp(10))
        self.toggle_trend = SketchButton(text="[b]Toggle Trend Line[/b]", markup=True, size_hint=(0.5, 1), font_size='16sp', font_name=HANDWRITTEN_FONT)
        self.toggle_trend.bind(on_press=self.toggle_trend_line)
        actions_layout.add_widget(self.toggle_trend)
        self.share_button = SketchButton(text="[b]Share w/ Doctor[/b]", markup=True, size_hint=(0.5, 1), font_size='18sp', font_name=HANDWRITTEN_FONT)
        self.share_button.bind(on_press=self.share_with_doctor)
        actions_layout.add_widget(self.share_button)
        self.add_widget(actions_layout)

        # For graph data tracking
        self.time_elapsed = []
        self.readings = []
        self.start_time = time.time()

        # Auto-update sensor every 30 seconds
        Clock.schedule_interval(self.update_sensor_reading, 30)

        self.readings = []
        self.timestamps = []
        self.start_time = time.time()
        
    def toggle_trend_line(self, instance):
        print("Trend line toggle clicked (feature not implemented yet)")

    def update_sensor_reading(self, instance):
        try:
            reading = sensor_input.read_sensor_data()
        except AttributeError: # If sensor_input.py is missing or function name differs
            import random
            reading = round(random.uniform(0.6, 1.3), 2) # Normal creatinine range
            if random.random() < 0.05: # Occasional spike for visual interest
                reading = round(random.uniform(1.5, 2.5), 2)


        self.creatinine_label.text = f"[b][color={SKETCH_COLOR_HEX}]Creatinine:[/color][/b] [b]{reading} mg/dL[/b]"

        current_time = round(time.time() - self.start_time, 2)
        self.readings.append(reading)
        self.timestamps.append(current_time)

        # Ensure CreatinineGraph can handle sketch-style plotting
        self.graph.update_graph(self.timestamps[-60:], self.readings[-60:]) # last 6