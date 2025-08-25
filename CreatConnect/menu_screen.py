### # menu_screen.py
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, Line, Ellipse
from kivy.metrics import dp
from kivy.app import App
from kivy.clock import Clock
from kivy.properties import StringProperty 
from kivy.core.text import Label as CoreLabel
import time
from graph import CreatinineGraph
from port_finder_rodeo import find_rodeostat_port_by_device_id


# Constants
SKETCH_COLOR = (0.2, 0.2, 0.2, 1)  # Dark grey for sketch lines
SKETCH_COLOR_HEX = "333333"
HANDWRITTEN_FONT = "Exo2-Bold.otf"

def rgb_to_hex(rgb_tuple):
    """Convert RGB tuple to hex string"""
    r, g, b, a = rgb_tuple
    return f"{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"

# Status highlight colors
STATUS_HIGHLIGHT_HIGH_COLOR = (1, 0, 0, 0.3)  # Red with transparency
STATUS_HIGHLIGHT_NORMAL_COLOR = (0, 1, 0, 0.3)  # Green with transparency  
STATUS_HIGHLIGHT_LOW_COLOR = (1, 0.5, 0, 0.3)  # Orange with transparency
STATUS_HIGHLIGHT_NONE_COLOR = (0, 0, 0, 0)  # Transparent

# Sketch line width
SKETCH_LINE_WIDTH = 2

# === Data source switch for your team ===
DATA_SOURCE = "potentiostat"   # or "simulation"

# === Potentiostat CV config ===
RODEO_DEVICE_ID = 42           # the number you set in Step 1
PSTAT_CURR_RANGE = "100uA"
PSTAT_SAMPLE_PERIOD_MS = 10
PSTAT_PARAMS = {
    "quietValue": 0.0,
    "quietTime": 1000,
    "amplitude": 0.4,
    "offset": 0.0,
    "period": 1000,
    "numCycles": 2,
    "shift": 0.0
}

class NavButton(BoxLayout):
    def __init__(self, text, icon, callback, **kwargs):
        super().__init__(orientation='vertical', spacing=dp(5), **kwargs)
        
        # Icon image (if provided) or text emoji
        if icon and icon.endswith('.png'):
            # Use image icon with centering
            icon_container = AnchorLayout(anchor_x='center', anchor_y='center', size_hint=(1, None), height=dp(24))
            icon_widget = Image(source=icon, size_hint=(None, None), size=(dp(24), dp(24)))
            icon_container.add_widget(icon_widget)
            self.add_widget(icon_container)
        else:
            # Use text emoji
            icon_label = Label(text=icon, font_size='16sp', size_hint=(1, None), height=dp(24))
            self.add_widget(icon_label)
        
        # Text label
        text_label = Label(text=text, font_size='12sp', font_name='Roboto', color=(0.5, 0.5, 0.5, 1), 
                          size_hint=(1, None), height=dp(20))
        
        self.add_widget(text_label)
        
        # Make clickable
        self.bind(on_touch_down=self._on_touch_down)
        self.callback = callback
    
    def _on_touch_down(self, instance, touch):
        if self.collide_point(*touch.pos):
            if self.callback:
                self.callback(self)
            return True
        return False

# --- Configuration for Sketch Style ---
# SKETCH_LINE_WIDTH = 1.5
# SKETCH_COLOR = (0.2, 0.2, 0.2, 1)
# PAPER_COLOR = (0.95, 0.95, 0.9, 1)
# HIGHLIGHT_COLOR = (0.5, 0.7, 0.9, 1) 

# Define specific highlight colors for the status bar
# STATUS_HIGHLIGHT_HIGH_COLOR = (0.8, 0.2, 0.2, 0.5) # Semi-transparent Red
# STATUS_HIGHLIGHT_NORMAL_COLOR = (0.2, 0.7, 0.2, 0.5) # Semi-transparent Green
# STATUS_HIGHLIGHT_LOW_COLOR = (0.9, 0.5, 0.1, 0.5) # Semi-transparent Orange/Yellow
# STATUS_HIGHLIGHT_NONE_COLOR = (0.0, 0.0, 0.0, 0.0) # Fully transparent when no highlight

# Helper to convert RGB tuple to hex string for Kivy markup
# def rgb_to_hex(rgb_tuple):
#     return f"{int(rgb_tuple[0]*255):02x}{int(rgb_tuple[1]*255):02x}{int(rgb_tuple[2]*255):02x}"

# SKETCH_COLOR_HEX = rgb_to_hex(SKETCH_COLOR)
# HIGHLIGHT_COLOR_HEX = rgb_to_hex(HIGHLIGHT_COLOR)

# Set default font 
# HANDWRITTEN_FONT = 'Roboto'

# --- Custom SketchButton Widget ---
class SketchButton(Button):
    FIXED_SKETCH_OFFSET_X = dp(2)
    FIXED_SKETCH_OFFSET_Y = dp(2)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.color = SKETCH_COLOR # Set text color

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
            self.sketch_color.rgb = (0.5, 0.7, 0.9) # Example highlight color
        else:
            self.sketch_color.rgb = SKETCH_COLOR


# Status Color Bar with numerical labels and dynamic highlight
class StatusColorBar(Widget):
    current_status_category = StringProperty('none') # 'high', 'normal', 'low', 'none'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.red_range_text = "High (>1.3)"
        self.green_range_text = "Normal (0.6-1.3)"
        self.orange_range_text = "Low (<0.6)"

        with self.canvas:
            # These rectangles will be redrawn in update_graphics
            self.red_rect = Rectangle()
            self.green_rect = Rectangle()
            self.orange_rect = Rectangle()
            
            self.bar_border_primary = Line(points=[], width=SKETCH_LINE_WIDTH)
            self.bar_border_offset = Line(points=[], width=SKETCH_LINE_WIDTH * 0.7)

            # Highlight rectangle
            # Initialize with a transparent color
            self.highlight_color = Color(*STATUS_HIGHLIGHT_NONE_COLOR) 
            self.highlight_rect = Rectangle()

            # Store references to the texture and the Rectangle that will draw it
            self.red_label_texture = None
            self.green_label_texture = None
            self.orange_label_texture = None

            self.red_label_rect = Rectangle()
            self.green_label_rect = Rectangle()
            self.orange_label_rect = Rectangle()

        self.bind(pos=self.update_graphics, size=self.update_graphics,
                  current_status_category=self.update_graphics) # Bind to new property
        self.update_graphics() # Initial draw

    def update_graphics(self, *args):
        # DEBUG PRINT: Confirm update_graphics is called and what status it has
        print(f"StatusColorBar: update_graphics called. current_status_category: {self.current_status_category}")

        self.canvas.clear() # Clear canvas to redraw everything
        x, y = self.pos
        w, h = self.size
        
        segment_height = h / 3
        
        # Redraw colored rectangles
        with self.canvas:
            Color(0.8, 0.2, 0.2, 1) # Muted red
            self.red_rect.pos = (x, y + 2 * segment_height)
            self.red_rect.size = (w, segment_height)
            
            Color(0.2, 0.7, 0.2, 1) # Muted green
            self.green_rect.pos = (x, y + segment_height)
            self.green_rect.size = (w, segment_height)
            
            Color(0.9, 0.5, 0.1, 1) # Muted orange
            self.orange_rect.pos = (x, y)
            self.orange_rect.size = (w, segment_height)

            # Sketch border for the whole bar - primary outline
            Color(*SKETCH_COLOR)
            offset_x = dp(2)
            offset_y = dp(2)

            self.bar_border_primary = Line(
                points=[x, y, x + w, y, x + w, y + h, x, y + h, x, y],
                width=SKETCH_LINE_WIDTH
            )

            self.bar_border_offset = Line(
                points=[
                    x + offset_x, y + offset_y,
                    x + w + offset_x, y + offset_y,
                    x + w + offset_x, y + h + offset_y,
                    x + offset_x, y + h + offset_y,
                    x + offset_x, y + offset_y
                ],
                width=SKETCH_LINE_WIDTH * 0.7
            )

            # Generate and draw labels using CoreLabel for texture
            label_margin_x = dp(5) # Margin from the right edge of the bar
            
            font_size_val = int(dp(10)) 
            text_size = (dp(70), None) # Desired width for text wrapping

            # Red Label
            label_red = CoreLabel(
                text=self.red_range_text,
                font_size=font_size_val, # Use the numeric font size
                font_name=HANDWRITTEN_FONT, # Use custom font
                color=SKETCH_COLOR + (1,), # Ensure alpha is 1
                halign='left',
                valign='middle',
                text_size=text_size
            )
            label_red.refresh() # Generate the texture
            self.red_label_texture = label_red.texture
            self.red_label_rect.texture = self.red_label_texture
            self.red_label_rect.size = self.red_label_texture.size
            self.red_label_rect.pos = (x + w + label_margin_x, y + 2 * segment_height + segment_height / 2 - self.red_label_texture.height / 2)
            self.canvas.add(self.red_label_rect)


            # Green Label
            label_green = CoreLabel(
                text=self.green_range_text,
                font_size=font_size_val, # Use the numeric font size
                font_name=HANDWRITTEN_FONT,
                color=SKETCH_COLOR + (1,),
                halign='left',
                valign='middle',
                text_size=text_size
            )
            label_green.refresh()
            self.green_label_texture = label_green.texture
            self.green_label_rect.texture = self.green_label_texture
            self.green_label_rect.size = self.green_label_texture.size
            self.green_label_rect.pos = (x + w + label_margin_x, y + segment_height + segment_height / 2 - self.green_label_texture.height / 2)
            self.canvas.add(self.green_label_rect)

            # Orange Label
            label_orange = CoreLabel(
                text=self.orange_range_text,
                font_size=font_size_val, # Use the numeric font size
                font_name=HANDWRITTEN_FONT,
                color=SKETCH_COLOR + (1,),
                halign='left',
                valign='middle',
                text_size=text_size
            )
            label_orange.refresh()
            self.orange_label_texture = label_orange.texture
            self.orange_label_rect.texture = self.orange_label_texture
            self.orange_label_rect.size = self.orange_label_texture.size
            self.orange_label_rect.pos = (x + w + label_margin_x, y + segment_height / 2 - self.orange_label_texture.height / 2)
            self.canvas.add(self.orange_label_rect)

            # Draw Highlight based on current_status_category
            if self.current_status_category == 'high':
                self.highlight_color.rgba = STATUS_HIGHLIGHT_HIGH_COLOR
                self.highlight_rect.pos = self.red_rect.pos
                self.highlight_rect.size = self.red_rect.size
                self.canvas.add(self.highlight_color)
                self.canvas.add(self.highlight_rect)
                print("StatusColorBar: Highlighted HIGH section with RED.") # DEBUG
            elif self.current_status_category == 'normal':
                self.highlight_color.rgba = STATUS_HIGHLIGHT_NORMAL_COLOR
                self.highlight_rect.pos = self.green_rect.pos
                self.highlight_rect.size = self.green_rect.size
                self.canvas.add(self.highlight_color)
                self.canvas.add(self.highlight_rect)
                print("StatusColorBar: Highlighted NORMAL section with GREEN.") # DEBUG
            elif self.current_status_category == 'low':
                self.highlight_color.rgba = STATUS_HIGHLIGHT_LOW_COLOR
                self.highlight_rect.pos = self.orange_rect.pos
                self.highlight_rect.size = self.orange_rect.size
                self.canvas.add(self.highlight_color)
                self.canvas.add(self.highlight_rect)
                print("StatusColorBar: Highlighted LOW section with ORANGE/YELLOW.") # DEBUG
            else:
                self.highlight_color.rgba = STATUS_HIGHLIGHT_NONE_COLOR # Make it fully transparent
                self.highlight_rect.size = (0, 0) # Hide highlight if status is 'none' or unknown
                print("StatusColorBar: No section highlighted (status 'none' or unknown).") # DEBUG


class MenuScreen(BoxLayout):
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

        self.add_widget(Widget(size_hint_y=None, height=dp(20)))
        # Add spacer after title
        self.add_widget(Widget(size_hint_y=None, height=dp(60)))

        # Main Content Area (Status Bar, Status Label, Breakdown)
        main_content = BoxLayout(orientation='vertical', size_hint=(1, 1), spacing=dp(-10))
        
        # Add top spacer to move content down
        main_content.add_widget(Widget(size_hint_y=None, height=dp(50)))
        
        # Status Label
        self.status_label = Label(text=f"[b][color={SKETCH_COLOR_HEX}]Status:[/color][/b] . . .", markup=True,
                                   font_size='18sp', font_name='Roboto', size_hint=(1, None), height=dp(30))
        self.status_label.bind(size=self.status_label.setter('text_size'))
        main_content.add_widget(self.status_label)
        
        # Status Bar
        status_bar_container = AnchorLayout(anchor_x='center', anchor_y='center', size_hint=(1, 0.3))
        self.status_bar = StatusColorBar(size_hint=(None, None), size=(dp(70), dp(220)))
        status_bar_container.add_widget(self.status_bar)
        main_content.add_widget(status_bar_container)
        
        # Add spacer between status bar and buttons
        main_content.add_widget(Widget(size_hint_y=None, height=dp(160)))
        
        # Action Buttons Section
        action_buttons = BoxLayout(orientation='horizontal', size_hint=(1, None), height=dp(60), spacing=dp(40))
        
        # Read Sensor Button
        read_sensor_btn = SketchButton(text="[b]Read Sensor[/b]", markup=True, size_hint=(1, 1),
                                        font_size='16sp', font_name='Roboto')
        read_sensor_btn.bind(on_release=self.start_read_sensor)
        action_buttons.add_widget(read_sensor_btn)
        
        # Reset Sensor Button
        reset_btn = SketchButton(text="[b]Reset Sensor[/b]", markup=True, size_hint=(1, 1),
                         font_size='16sp', font_name='Roboto')
        reset_btn.bind(on_release=self.reset_sensor_readings)
        action_buttons.add_widget(reset_btn)
        
        main_content.add_widget(action_buttons)
        main_content.add_widget(Widget(size_hint_y=None, height=dp(20)))
        main_content.add_widget(Widget(size_hint_y=None, height=dp(20)))

        # Add spacer between buttons and breakdown
        main_content.add_widget(Widget(size_hint_y=None, height=dp(20)))
        
        # Breakdown Label (below buttons)
        self.breakdown_label = Label(text=f"[color={SKETCH_COLOR_HEX}]Breakdown: No data yet.[/color]", markup=True,
                                font_size='15sp', font_name='Roboto',
                                halign='left', valign='top', size_hint_y=None, height=dp(100))
        self.breakdown_label.bind(size=self.breakdown_label.setter('text_size'))
        main_content.add_widget(self.breakdown_label)
        
        # Add flexible spacer to push content up
       # main_content.add_widget(Widget())
        
        self.add_widget(main_content)

        # Bottom Navigation Bar
        bottom_nav = BoxLayout(orientation='horizontal', size_hint=(1, None), height=dp(80), 
                              spacing=dp(10), padding=[dp(10), dp(10), dp(10), dp(10)])
        
        # Navigation Icons with proper icons
        nav_items = [
            ("History Log", "history_icon.png", self.go_to_history_log),
            ("Sensor Graph", "graph_icon.png", self.go_to_sensor_graph),
            ("Health Info", "health_info.png", self.go_to_health_info),
            ("Contact Doctor", "contact_doctor.png", self.contact_doctor)
        ]
        
        for text, icon, callback in nav_items:
            nav_item = NavButton(text=text, icon=icon, callback=callback)
            bottom_nav.add_widget(nav_item)

        self.add_widget(bottom_nav)

        # Bind to screen entry to update status
        self.bind(on_kv_post=self._on_kv_post) # This event fires when the widget is fully built and added

    def start_sensor_simulation(self, instance):
        from sensor_input import read_simulated_sensor_data
        app = App.get_running_app()

        # Load simulated data
        result = read_simulated_sensor_data()
        app.simulated_df = result["data"]
        app.simulated_file = result["file"]
        app.sim_creatinine = result["creatinine"]
        app.sim_status = result["status"]
        app.sim_peak_signal = result["peak_signal"]

        # ✅ Add the new creatinine value to the log
        app.all_creatinine_readings.append(app.sim_creatinine)

        # ✅ Schedule status update for menu screen immediately
        Clock.schedule_once(lambda dt: self.update_menu_status(), 0.1)

        app.sim_index = 0
        app.sim_start_time = time.time()

        # Navigate to Sensor Graph screen
        app.root.current = 'sensor_graph_screen'

        # Start simulation on the Sensor Graph screen
        Clock.schedule_once(app.root.get_screen('sensor_graph_screen').children[0].update_sensor_reading, 0)




    def reset_sensor_readings(self, instance):
        app = App.get_running_app()
    
        # Clear readings
        app.all_creatinine_readings.clear()

        # Reset labels and status color bar
        self.status_label.text = f"[b][color={SKETCH_COLOR_HEX}]Status:[/color][/b] . . ."
        self.breakdown_label.text = f"[color={SKETCH_COLOR_HEX}]Breakdown: No data yet.[/color]"
        self.status_bar.current_status_category = 'none'
        try:
            sensor_screen_widget = app.root.get_screen('sensor_graph_screen').children[0]
            sensor_screen_widget.graph.clear()
            sensor_screen_widget.status_label.text = "[b][color=000000]Status:[/color][/b] [b]--[/b]"
            sensor_screen_widget.creatinine_label.text = "[b][color=000000]Creatinine: -- mg/dL[/color][/b]"
            print("✅ Sensor graph screen cleared.")
        except Exception as e:
            print(f"❌ Failed to clear sensor screen: {e}")
        
        # Update status message
        self.status_label.text = f"[b][color={SKETCH_COLOR_HEX}]Status:[/color][/b] [b]Reset Complete[/b]"
        self.breakdown_label.text = f"[color={SKETCH_COLOR_HEX}]Breakdown: All readings cleared. Ready for new data.[/color]"

    def _on_kv_post(self, instance):
        # Schedule update to happen after the widget is fully laid out
        # This prevents issues with initial size/pos not being set yet
        Clock.schedule_once(self.update_menu_status, 0)

    def update_menu_status(self, *args):
        from sensor_input import load_health_info
        from personalization import get_status, get_breakdown

        app = App.get_running_app()
    
        if not app.all_creatinine_readings:
            # No data yet
            self.status_label.text = f"[b][color={SKETCH_COLOR_HEX}]Status:[/color][/b] [b]No Data Yet[/b]"
            self.breakdown_label.text = f"[color={SKETCH_COLOR_HEX}][b]Breakdown:[/b]\n• Data not yet available.\n• Read sensor for an update.[/color]"
            self.status_bar.current_status_category = 'none'
            return

        latest_creatinine = app.all_creatinine_readings[-1]
        print(f"MenuScreen: Updating status. Latest creatinine: {latest_creatinine:.2f}")
    
        # Load health info
        info = load_health_info()
        age = info["age"]
        weight = info["weight"]
        gender = info["gender"]

        # Get personalized status
        status = get_status(latest_creatinine, age, gender, weight)
        breakdown = get_breakdown(status, age, gender, weight)

        # Color settings
        status_color = {
            "High": "cc0000",
            "Low": "ff9900",
            "Normal": "00aa00"
        }.get(status, SKETCH_COLOR_HEX)

        status_category = {
            "High": "high",
            "Low": "low",
            "Normal": "normal"
        }.get(status, "none")

        # Update status label
        self.status_label.text = f"[b][color={SKETCH_COLOR_HEX}]Status:[/color][/b] [b][color={status_color}]{status}[/color][/b]"

        # Update breakdown label with personalized breakdown
        self.breakdown_label.text = f"[color={SKETCH_COLOR_HEX}][b]Breakdown:[/b]\n• {breakdown}[/color]"

        # Update status bar highlight
        self.status_bar.current_status_category = status_category


    def go_to_sensor_graph(self, instance):
        print("MenuScreen: Sensor Graph button clicked!")
        app = App.get_running_app()
        print(f"MenuScreen: Current screen before navigation: {app.root.current}")
        print(f"MenuScreen: Available screens: {[screen.name for screen in app.root.screens]}")
        
        try:
            app.root.current = 'sensor_graph_screen'
            print(f"MenuScreen: Successfully navigated to sensor_graph_screen. Current screen: {app.root.current}")
            
        except Exception as e:
            print(f"MenuScreen: Error navigating to sensor graph: {e}")

    def go_to_history_log(self, instance):
        print("MenuScreen: History Log button clicked!")
        app = App.get_running_app()
        try:
            app.root.current = 'history_log_screen'
            print(f"MenuScreen: Successfully navigated to history_log_screen. Current screen: {app.root.current}")
        except Exception as e:
            print(f"MenuScreen: Error navigating to history log screen: {e}")

    def go_to_health_info(self, instance):
        print("MenuScreen: Health Info button clicked!")
        app = App.get_running_app()
        try:
            app.root.current = 'health_info_screen'
            print(f"MenuScreen: Successfully navigated to health_info_screen. Current screen: {app.root.current}")
        except Exception as e:
            print(f"MenuScreen: Error navigating to health info screen: {e}")

    def contact_doctor(self, instance):
        print("Contacting doctor (feature not implemented yet)")

    def share_with_doctor(self, instance):
        print("Sharing with doctor (feature not implemented yet)")

    def start_read_sensor(self, instance):
        app = App.get_running_app()
        app.root.current = 'sensor_graph_screen'
        sensor_ui = app.root.get_screen('sensor_graph_screen').children[0]

        if DATA_SOURCE == "potentiostat":
            try:
                port = find_rodeostat_port_by_device_id(RODEO_DEVICE_ID)
                sensor_ui.start_pstat_cv(
                    port=port,
                    params=PSTAT_PARAMS,
                    curr_range=PSTAT_CURR_RANGE,
                    sample_period_ms=PSTAT_SAMPLE_PERIOD_MS
                )
                self.status_bar.current_status_category = 'none'
                self.status_label.text = f"[b][color={SKETCH_COLOR_HEX}]Status:[/color][/b] [b]Running CV...[/b]"
                self.breakdown_label.text = f"[color={SKETCH_COLOR_HEX}]Breakdown: potentiostat test in progress.[/color]"
            except Exception as e:
                print(f"❌ Could not start potentiostat: {e}")
                self.status_label.text = f"[b][color={SKETCH_COLOR_HEX}]Status:[/color][/b] [b]Device not found[/b]"
                # Optional: fallback to your simulation
                # self.start_sensor_simulation(instance)
        else:
            self.start_sensor_simulation(instance)

