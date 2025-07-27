from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, Rectangle, Line
from kivy.metrics import dp
from kivy.app import App
from kivy.properties import StringProperty
from kivy.core.text import LabelBase
import json
import os
from datetime import datetime

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

class HistoryEntryWidget(BoxLayout):
    def __init__(self, date, time, creatinine_value, **kwargs):
        super().__init__(orientation='horizontal', size_hint=(1, None), height=dp(60), spacing=dp(10), **kwargs)
        
        # Date and Time
        datetime_container = BoxLayout(orientation='vertical', size_hint=(0.4, 1), spacing=dp(2))
        date_label = Label(text=date, font_size='14sp', font_name='Roboto', 
                          color=SKETCH_COLOR, size_hint=(1, None), height=dp(25))
        time_label = Label(text=time, font_size='12sp', font_name='Roboto', 
                          color=(0.5, 0.5, 0.5, 1), size_hint=(1, None), height=dp(20))
        datetime_container.add_widget(date_label)
        datetime_container.add_widget(time_label)
        
        # Creatinine Value
        creatinine_container = BoxLayout(orientation='vertical', size_hint=(0.3, 1), spacing=dp(2))
        creatinine_label = Label(text="Creatinine", font_size='12sp', font_name='Roboto', 
                               color=(0.5, 0.5, 0.5, 1), size_hint=(1, None), height=dp(20))
        value_label = Label(text=f"{creatinine_value:.2f} mg/dL", font_size='16sp', font_name='Roboto', 
                           color=SKETCH_COLOR, size_hint=(1, None), height=dp(30))
        creatinine_container.add_widget(creatinine_label)
        creatinine_container.add_widget(value_label)
        
        # Status indicator
        status_container = BoxLayout(orientation='vertical', size_hint=(0.3, 1), spacing=dp(2))
        status_label = Label(text="Status", font_size='12sp', font_name='Roboto', 
                            color=(0.5, 0.5, 0.5, 1), size_hint=(1, None), height=dp(20))
        
        # Determine status based on creatinine value
        if creatinine_value > 1.3:
            status_text = "High"
            status_color = (0.8, 0, 0, 1)  # Red
        elif creatinine_value < 0.6:
            status_text = "Low"
            status_color = (1, 0.5, 0, 1)  # Orange
        else:
            status_text = "Normal"
            status_color = (0, 0.7, 0, 1)  # Green
            
        status_value = Label(text=status_text, font_size='14sp', font_name='Roboto', 
                            color=status_color, size_hint=(1, None), height=dp(30))
        status_container.add_widget(status_label)
        status_container.add_widget(status_value)
        
        self.add_widget(datetime_container)
        self.add_widget(creatinine_container)
        self.add_widget(status_container)

class HistoryLogScreen(BoxLayout):
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
        page_title = Label(text="History Log", font_size='24sp', font_name='Roboto',
                          color=SKETCH_COLOR, size_hint=(1, None), height=dp(40))
        main_content.add_widget(page_title)
        
        # Header Row
        header_container = BoxLayout(orientation='horizontal', size_hint=(1, None), height=dp(40), spacing=dp(10))
        
        date_header = Label(text="Date & Time", font_size='14sp', font_name='Roboto',
                           color=SKETCH_COLOR, size_hint=(0.4, 1))
        creatinine_header = Label(text="Creatinine", font_size='14sp', font_name='Roboto',
                                color=SKETCH_COLOR, size_hint=(0.3, 1))
        status_header = Label(text="Status", font_size='14sp', font_name='Roboto',
                            color=SKETCH_COLOR, size_hint=(0.3, 1))
        
        header_container.add_widget(date_header)
        header_container.add_widget(creatinine_header)
        header_container.add_widget(status_header)
        main_content.add_widget(header_container)
        
        # Scrollable History List
        scroll_container = BoxLayout(orientation='vertical', size_hint=(1, 1))
        
        # Create scroll view for history entries
        self.scroll_view = ScrollView(size_hint=(1, 1))
        self.history_layout = GridLayout(cols=1, spacing=dp(5), size_hint_y=None)
        self.history_layout.bind(minimum_height=self.history_layout.setter('height'))
        
        self.scroll_view.add_widget(self.history_layout)
        scroll_container.add_widget(self.scroll_view)
        main_content.add_widget(scroll_container)
        
        # Buttons
        button_container = BoxLayout(orientation='horizontal', size_hint=(1, None), height=dp(60), spacing=dp(20))
        
        clear_btn = SketchButton(text="Clear History", size_hint=(1, 1),
                                font_size='16sp', font_name='Roboto')
        clear_btn.bind(on_release=self.clear_history)
        
        back_btn = SketchButton(text="Back to Menu", size_hint=(1, 1),
                               font_size='16sp', font_name='Roboto')
        back_btn.bind(on_release=self.go_back_to_menu)
        
        button_container.add_widget(clear_btn)
        button_container.add_widget(back_btn)
        main_content.add_widget(button_container)
        
        # Status message
        self.status_label = Label(text="", font_size='14sp', font_name='Roboto',
                                 color=SKETCH_COLOR, size_hint=(1, None), height=dp(30))
        main_content.add_widget(self.status_label)
        
        self.add_widget(main_content)

        # Load history data
        self.load_history()

    def load_history(self):
        """Load and display history data"""
        try:
            # Clear existing entries
            self.history_layout.clear_widgets()
            
            # Load from app's creatinine readings
            app = App.get_running_app()
            print(f"🔍 History Log - Checking app readings: {getattr(app, 'all_creatinine_readings', 'Not found')}")
            if hasattr(app, 'all_creatinine_readings') and app.all_creatinine_readings:
                # Display all readings in reverse chronological order (newest first)
                total_readings = len(app.all_creatinine_readings)
                
                for i, creatinine_value in enumerate(reversed(app.all_creatinine_readings)):
                    # Calculate time offset for each reading
                    # Most recent reading = current time
                    # Older readings = progressively earlier times
                    reading_time = datetime.now()
                    if i > 0:  # Not the most recent reading
                        # Subtract time based on how many readings back this is
                        from datetime import timedelta
                        # Each reading is 5 minutes apart, going backwards in time
                        minutes_back = i * 5
                        reading_time = reading_time - timedelta(minutes=minutes_back)
                    
                    # Create history entry
                    entry = HistoryEntryWidget(
                        date=reading_time.strftime("%Y-%m-%d"),
                        time=reading_time.strftime("%H:%M:%S"),
                        creatinine_value=creatinine_value
                    )
                    self.history_layout.add_widget(entry)
                
                latest_creatinine = app.all_creatinine_readings[-1]
                self.status_label.text = f"Total readings: {total_readings} | Latest: {latest_creatinine:.2f} mg/dL"
                self.status_label.color = (0, 0.7, 0, 1)  # Green
            else:
                self.status_label.text = "No history data available"
                self.status_label.color = (0.5, 0.5, 0.5, 1)  # Gray
                
        except Exception as e:
            self.status_label.text = f"Error loading history: {str(e)}"
            self.status_label.color = (0.8, 0, 0, 1)  # Red

    def clear_history(self, instance):
        """Clear all history data"""
        try:
            app = App.get_running_app()
            if hasattr(app, 'all_creatinine_readings'):
                app.all_creatinine_readings.clear()
            
            # Clear the display
            self.history_layout.clear_widgets()
            
            self.status_label.text = "All history cleared successfully!"
            self.status_label.color = (0, 0.7, 0, 1)  # Green
            
        except Exception as e:
            self.status_label.text = f"Error clearing history: {str(e)}"
            self.status_label.color = (0.8, 0, 0, 1)  # Red

    def go_back_to_menu(self, instance):
        """Navigate back to the main menu"""
        app = App.get_running_app()
        app.root.current = 'menu_screen' 