from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.image import Image
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, Line
from kivy.metrics import dp
from kivy.app import App
from kivy.properties import StringProperty
from kivy.core.text import LabelBase
import json
import os

# Constants
SKETCH_COLOR = (0.2, 0.2, 0.2, 1)  # Dark grey for sketch lines
SKETCH_COLOR_HEX = "333333"
HANDWRITTEN_FONT = "Exo2-Bold.otf"
SKETCH_LINE_WIDTH = 2

class SketchButton(Button):
    FIXED_SKETCH_OFFSET_X = dp(2)
    FIXED_SKETCH_OFFSET_Y = dp(2)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.color = SKETCH_COLOR

        with self.canvas.before:
            self.sketch_color = Color(*SKETCH_COLOR)
            self.sketch_border_lines = Line(points=[], width=SKETCH_LINE_WIDTH)

        self.bind(pos=self.update_graphics, size=self.update_graphics)

    def update_graphics(self, *args):
        x, y = self.pos
        w, h = self.size

        self.canvas.before.clear()
        with self.canvas.before:
            self.sketch_color = Color(*SKETCH_COLOR)

            self.sketch_border_lines = Line(
                points=[
                    x, y,
                    x + w, y,
                    x + w, y + h,
                    x, y + h,
                    x, y
                ],
                width=SKETCH_LINE_WIDTH
            )
            
            self.sketch_border_lines_offset = Line(
                points=[
                    x + self.FIXED_SKETCH_OFFSET_X, y + self.FIXED_SKETCH_OFFSET_Y,
                    x + w + self.FIXED_SKETCH_OFFSET_X, y + self.FIXED_SKETCH_OFFSET_Y,
                    x + w + self.FIXED_SKETCH_OFFSET_X, y + h + self.FIXED_SKETCH_OFFSET_Y,
                    x + self.FIXED_SKETCH_OFFSET_X, y + h + self.FIXED_SKETCH_OFFSET_Y,
                    x + self.FIXED_SKETCH_OFFSET_X, y + self.FIXED_SKETCH_OFFSET_Y
                ],
                width=SKETCH_LINE_WIDTH * 0.7
            )

        if self.state == 'down':
            self.sketch_color.rgb = (0.5, 0.7, 0.9)
        else:
            self.sketch_color.rgb = SKETCH_COLOR

class SketchTextInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (1, 1, 1, 1)
        self.foreground_color = SKETCH_COLOR
        self.font_name = 'Roboto'
        self.font_size = '16sp'
        self.multiline = False
        self.padding = [dp(10), dp(10)]
        self.cursor_color = SKETCH_COLOR
        
        with self.canvas.after:
            self.sketch_color = Color(*SKETCH_COLOR)
            self.sketch_border = Line(points=[], width=SKETCH_LINE_WIDTH)

        self.bind(pos=self.update_graphics, size=self.update_graphics)

    def update_graphics(self, *args):
        x, y = self.pos
        w, h = self.size

        self.canvas.after.clear()
        with self.canvas.after:
            self.sketch_color = Color(*SKETCH_COLOR)
            self.sketch_border = Line(
                points=[
                    x, y,
                    x + w, y,
                    x + w, y + h,
                    x, y + h,
                    x, y
                ],
                width=SKETCH_LINE_WIDTH
            )

class SketchSpinner(Spinner):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (1, 1, 1, 1)
        self.color = SKETCH_COLOR
        self.font_name = 'Roboto'
        self.font_size = '16sp'
        
        with self.canvas.before:
            self.sketch_color = Color(*SKETCH_COLOR)
            self.sketch_border = Line(points=[], width=SKETCH_LINE_WIDTH)

        self.bind(pos=self.update_graphics, size=self.update_graphics)

    def update_graphics(self, *args):
        x, y = self.pos
        w, h = self.size

        self.canvas.before.clear()
        with self.canvas.before:
            self.sketch_color = Color(*SKETCH_COLOR)
            self.sketch_border = Line(
                points=[
                    x, y,
                    x + w, y,
                    x + w, y + h,
                    x, y + h,
                    x, y
                ],
                width=SKETCH_LINE_WIDTH
            )

class HealthInfoScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', spacing=dp(15), padding=dp(15), **kwargs)

        # Title and Logo section
        title_section = BoxLayout(orientation='vertical', size_hint=(1, None), height=dp(120), padding=[dp(10), dp(0)], spacing=dp(5))
        logo_container = AnchorLayout(anchor_x="left", anchor_y="center", size_hint=(1, None), height=dp(80))
        logo = Image(source='FinalLogo.png', size_hint=(None,None), size=(dp(220),dp(80)))
        logo_container.add_widget(logo)
        title_section.add_widget(logo_container) 
        self.title_label = Label(text="CreatConnect", font_size='24sp', font_name='Roboto',
                                     halign='left', valign='middle', color=SKETCH_COLOR, size_hint=(1, None), height=dp(30))
        self.title_label.bind(size=self.title_label.setter('text_size'))
        title_section.add_widget(self.title_label)
        self.add_widget(title_section)

        # Add spacer
        self.add_widget(Widget(size_hint_y=None, height=dp(20)))

        # Main Content Area
        main_content = BoxLayout(orientation='vertical', size_hint=(1, 1), spacing=dp(20))
        
        # Page Title
        page_title = Label(text="Health Information", font_size='24sp', font_name='Roboto',
                          color=SKETCH_COLOR, size_hint=(1, None), height=dp(40))
        main_content.add_widget(page_title)
        
        # Form Fields
        form_container = BoxLayout(orientation='vertical', size_hint=(1, None), height=dp(300), spacing=dp(20))
        
        # Age Field
        age_container = BoxLayout(orientation='vertical', size_hint=(1, None), height=dp(80), spacing=dp(5))
        age_label = Label(text="Age (years):", font_size='16sp', font_name='Roboto',
                         color=SKETCH_COLOR, size_hint=(1, None), height=dp(25))
        self.age_input = SketchTextInput(hint_text="Enter your age", size_hint=(1, None), height=dp(50))
        age_container.add_widget(age_label)
        age_container.add_widget(self.age_input)
        form_container.add_widget(age_container)
        
        # Weight Field
        weight_container = BoxLayout(orientation='vertical', size_hint=(1, None), height=dp(80), spacing=dp(5))
        weight_label = Label(text="Weight (kg):", font_size='16sp', font_name='Roboto',
                           color=SKETCH_COLOR, size_hint=(1, None), height=dp(25))
        self.weight_input = SketchTextInput(hint_text="Enter your weight", size_hint=(1, None), height=dp(50))
        weight_container.add_widget(weight_label)
        weight_container.add_widget(self.weight_input)
        form_container.add_widget(weight_container)
        
        # Gender Field
        gender_container = BoxLayout(orientation='vertical', size_hint=(1, None), height=dp(80), spacing=dp(5))
        gender_label = Label(text="Gender:", font_size='16sp', font_name='Roboto',
                           color=SKETCH_COLOR, size_hint=(1, None), height=dp(25))
        self.gender_spinner = SketchSpinner(
            text='Select Gender',
            values=('Male', 'Female', 'Other'),
            size_hint=(1, None), height=dp(50)
        )
        gender_container.add_widget(gender_label)
        gender_container.add_widget(self.gender_spinner)
        form_container.add_widget(gender_container)
        
        main_content.add_widget(form_container)
        
        # Buttons
        button_container = BoxLayout(orientation='horizontal', size_hint=(1, None), height=dp(60), spacing=dp(20))
        
        save_btn = SketchButton(text="Save Information", size_hint=(1, 1),
                               font_size='16sp', font_name='Roboto')
        save_btn.bind(on_release=self.save_health_info)
        
        back_btn = SketchButton(text="Back to Menu", size_hint=(1, 1),
                               font_size='16sp', font_name='Roboto')
        back_btn.bind(on_release=self.go_back_to_menu)
        
        button_container.add_widget(save_btn)
        button_container.add_widget(back_btn)
        main_content.add_widget(button_container)
        
        # Status message
        self.status_label = Label(text="", font_size='14sp', font_name='Roboto',
                                 color=SKETCH_COLOR, size_hint=(1, None), height=dp(30))
        main_content.add_widget(self.status_label)
        
        self.add_widget(main_content)

        # Load existing data
        self.load_health_info()

    def save_health_info(self, instance):
        """Save health information to a JSON file"""
        try:
            health_data = {
                'age': self.age_input.text,
                'weight': self.weight_input.text,
                'gender': self.gender_spinner.text
            }
            
            # Save to file
            with open('health_info.json', 'w') as f:
                json.dump(health_data, f)
            
            self.status_label.text = "Health information saved successfully!"
            self.status_label.color = (0, 0.7, 0, 1)  # Green for success
            
        except Exception as e:
            self.status_label.text = f"Error saving data: {str(e)}"
            self.status_label.color = (0.8, 0, 0, 1)  # Red for error

    def load_health_info(self):
        """Load existing health information from JSON file"""
        try:
            if os.path.exists('health_info.json'):
                with open('health_info.json', 'r') as f:
                    health_data = json.load(f)
                
                self.age_input.text = health_data.get('age', '')
                self.weight_input.text = health_data.get('weight', '')
                self.gender_spinner.text = health_data.get('gender', 'Select Gender')
                
        except Exception as e:
            print(f"Error loading health info: {e}")

    def go_back_to_menu(self, instance):
        """Navigate back to the main menu"""
        app = App.get_running_app()
        app.root.current = 'menu_screen' 