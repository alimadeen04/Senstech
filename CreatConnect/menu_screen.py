### # menu_screen.py
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, Line
from kivy.metrics import dp
from kivy.app import App
from kivy.clock import Clock
from kivy.properties import StringProperty 
from kivy.core.text import Label as CoreLabel

# --- Configuration for Sketch Style ---
SKETCH_LINE_WIDTH = 1.5
SKETCH_COLOR = (0.2, 0.2, 0.2, 1)
PAPER_COLOR = (0.95, 0.95, 0.9, 1)
HIGHLIGHT_COLOR = (0.5, 0.7, 0.9, 1) 

# Define specific highlight colors for the status bar
STATUS_HIGHLIGHT_HIGH_COLOR = (0.8, 0.2, 0.2, 0.5) # Semi-transparent Red
STATUS_HIGHLIGHT_NORMAL_COLOR = (0.2, 0.7, 0.2, 0.5) # Semi-transparent Green
STATUS_HIGHLIGHT_LOW_COLOR = (0.9, 0.5, 0.1, 0.5) # Semi-transparent Orange/Yellow
STATUS_HIGHLIGHT_NONE_COLOR = (0.0, 0.0, 0.0, 0.0) # Fully transparent when no highlight

# Helper to convert RGB tuple to hex string for Kivy markup
def rgb_to_hex(rgb_tuple):
    return f"{int(rgb_tuple[0]*255):02x}{int(rgb_tuple[1]*255):02x}{int(rgb_tuple[2]*255):02x}"

SKETCH_COLOR_HEX = rgb_to_hex(SKETCH_COLOR)
HIGHLIGHT_COLOR_HEX = rgb_to_hex(HIGHLIGHT_COLOR)

# Set default font 
HANDWRITTEN_FONT = 'Roboto'

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
            self.sketch_color.rgb = HIGHLIGHT_COLOR
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
        title_section = BoxLayout(orientation='horizontal', size_hint=(1, None), height=dp(100), padding=[dp(10), dp(0)], spacing=dp(5))
        logo_container = AnchorLayout(anchor_x="left", anchor_y="center", size_hint=(None, 1), width=dp(220))
        logo = Image(source='FinalLogo.png', size_hint=(None,None), size=(dp(220),dp(80)))
        logo_container.add_widget(logo)
        title_section.add_widget(logo_container) 
        self.title_label = Label(text="CreatConnect", font_size='35sp', font_name=HANDWRITTEN_FONT,
                                     halign='left', valign='middle', color=SKETCH_COLOR, size_hint=(1, 1))
        self.title_label.bind(size=self.title_label.setter('text_size'))
        title_section.add_widget(self.title_label)
        self.add_widget(title_section)

        # Status Bar and Menu Options Layout (using a horizontal layout for main content)
        content_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.7), spacing=dp(20)) # Main content area

        # Left side: Status Bar and "Read Sensor" (mock, just for visual layout)
        left_panel = BoxLayout(orientation='vertical', size_hint=(0.4, 1), spacing=dp(10))
        
        # Status Label (mock, as it's the main screen)
        self.status_label = Label(text=f"[b][color={SKETCH_COLOR_HEX}]Status:[/color][/b] . . .", markup=True,
                                   font_size='18sp', font_name=HANDWRITTEN_FONT, size_hint=(1, None), height=dp(30))
        self.status_label.bind(size=self.status_label.setter('text_size'))
        left_panel.add_widget(self.status_label)
        left_panel.add_widget(Widget(size_hint_y=7))
        # Status Bar
        status_bar_container = AnchorLayout(anchor_x='center', anchor_y='center', size_hint=(1, 0.5))
        self.status_bar = StatusColorBar(size_hint=(None, None), size=(dp(70), dp(220)))
        status_bar_container.add_widget(self.status_bar)
        left_panel.add_widget(status_bar_container)
        left_panel.add_widget(Widget(size_hint_y=None, height=dp(100))) 



        # "Read Sensor" Button (mock, no actual reading here)
        read_sensor_btn = SketchButton(text="[b]Read Sensor[/b]", markup=True, size_hint=(1, None),
                                        height=dp(50), font_size='18sp', font_name=HANDWRITTEN_FONT)
        read_sensor_btn.bind(on_release=self.update_menu_status)
        left_panel.add_widget(read_sensor_btn)

        content_layout.add_widget(left_panel)

        # Reset Button
        reset_btn = SketchButton(text="[b]Reset Sensor[/b]", markup=True, size_hint=(1, None),
                         height=dp(50), font_size='18sp', font_name=HANDWRITTEN_FONT)
        reset_btn.bind(on_release=self.reset_sensor_readings)
        left_panel.add_widget(reset_btn)



        # Right side: Menu Options
        menu_options_layout = BoxLayout(orientation='vertical', size_hint=(0.4, .4), spacing=dp(15), padding=(dp(10), dp(0), dp(10), dp(0)))
        menu_options_layout.add_widget(Widget(size_hint_y=None, height=dp(50))) 
        menu_options_layout.add_widget(Label(text="[b]Menu Options[/b]", markup=True,
                                             font_size='18sp', font_name=HANDWRITTEN_FONT,
                                             halign='left', valign='bottom',
                                             color=SKETCH_COLOR, size_hint=(1, None), height=dp(30)))


        options = ["Call Doctor", "History Log", "Detailed History Graph", "Sensor Graph", "Health Info"]
        for opt in options:
            btn = SketchButton(text=opt, size_hint_y=None, height=dp(40),
                               font_name=HANDWRITTEN_FONT, font_size='16sp',
                               halign='center', text_size=(dp(250),None))

            # Bind 'Sensor Graph' to navigate to CreatConnectUI
            if opt == "Sensor Graph":
                btn.bind(on_release=self.go_to_sensor_graph)
            menu_options_layout.add_widget(btn)

        # Add a flexible spacer to push buttons to top
        # menu_options_layout.add_widget(Widget())

        content_layout.add_widget(menu_options_layout)

        self.add_widget(content_layout) # Add the main content layout

        # Bottom sections: Breakdown and Share
        # This breakdown label will be updated by update_menu_status
        self.breakdown_label = Label(text=f"[color={SKETCH_COLOR_HEX}]Breakdown: No data yet.[/color]", markup=True,
                                font_size='15sp', font_name=HANDWRITTEN_FONT,
                                halign='left', valign='top', size_hint_y=None, height=dp(100))
        self.breakdown_label.bind(size=self.breakdown_label.setter('text_size'))
        self.add_widget(self.breakdown_label)

        share_button = SketchButton(text="[b]Share with Doctor[/b]", markup=True, size_hint=(1, None),
                                     height=dp(50), font_size='18sp', font_name=HANDWRITTEN_FONT)
        share_button.bind(on_press=self.share_with_doctor) # implement this later
        self.add_widget(share_button)

        # Bind to screen entry to update status
        self.bind(on_kv_post=self._on_kv_post) # This event fires when the widget is fully built and added

    def reset_sensor_readings(self, instance):
        app = App.get_running_app()
    
        # Clear readings
        app.all_creatinine_readings.clear()

        # Reset labels and status color bar
        self.status_label.text = f"[b][color={SKETCH_COLOR_HEX}]Status:[/color][/b] . . ."
        self.breakdown_label.text = f"[color={SKETCH_COLOR_HEX}]Breakdown: No data yet.[/color]"
        self.status_bar.current_status_category = 'none'

        print("Sensor readings reset. Status and visuals cleared.")

    def _on_kv_post(self, instance):
        # Schedule update to happen after the widget is fully laid out
        # This prevents issues with initial size/pos not being set yet
        Clock.schedule_once(self.update_menu_status, 0)

    def update_menu_status(self, *args):
        app = App.get_running_app()
        
        # Calculate the average creatinine from all readings
        average_creatinine = 0.0
        if app.all_creatinine_readings:
            # Ensure app.all_creatinine_readings is not empty before calculating sum and average
            average_creatinine = sum(app.all_creatinine_readings) / len(app.all_creatinine_readings)
            
        print(f"MenuScreen: Updating status. Latest creatinine (for info): {app.all_creatinine_readings[-1]:.2f}" if app.all_creatinine_readings else "MenuScreen: No latest creatinine.") # Keep for debug
        print(f"MenuScreen: Updating status. Average creatinine: {average_creatinine:.2f}") # DEBUG PRINT
        
        status_text = "[b][color={}]Status:[/color][/b] ".format(SKETCH_COLOR_HEX)
        status_color = ""
        current_status_category = 'none' # Initialize for StatusColorBar
        breakdown_message = ""

        if average_creatinine > 1.3:
            current_status = "High"
            status_color = "cc0000" # Red for high
            current_status_category = 'high'
            breakdown_message = "[b]Breakdown:[/b]\n" \
                                 "• Your creatinine levels are [color=cc0000]higher than normal[/color] on average.\n" \
                                 "• Consult a healthcare professional for further evaluation."
        elif average_creatinine < 0.6 and app.all_creatinine_readings: # Ensure it's not the initial 0.0 placeholder before any readings
            current_status = "Low"
            status_color = "ff9900" # Orange for low
            current_status_category = 'low'
            breakdown_message = "[b]Breakdown:[/b]\n" \
                                 "• Your creatinine levels are [color=ff9900]lower than normal[/color] on average.\n" \
                                 "• Consult a healthcare professional for further evaluation."
        elif not app.all_creatinine_readings: # No data yet, or initial state
            current_status = "No Data Yet"
            status_color = SKETCH_COLOR_HEX # Use sketch color for no data
            current_status_category = 'none'
            breakdown_message = "[b]Breakdown:[/b]\n" \
                                 "• Data not yet available.\n" \
                                 "• Read sensor for an update."
        else: # Normal range (0.6 to 1.3, inclusive)
            current_status = "Normal"
            status_color = "00aa00" # Green for normal
            current_status_category = 'normal'
            breakdown_message = "[b]Breakdown:[/b]\n" \
                                 "• Your creatinine levels are within the normal range on average.\n" \
                                 "• No immediate abnormalities detected.\n" \
                                 "• Continue monitoring as advised by your doctor."
        
        self.status_label.text = status_text + f"[b][color={status_color}]{current_status}[/color][/b]"
        self.breakdown_label.text = f"[color={SKETCH_COLOR_HEX}]{breakdown_message}[/color]" # Update breakdown label

        # Update the StatusColorBar's current_status_category property
        self.status_bar.current_status_category = current_status_category
        print(f"MenuScreen: Set status_bar.current_status_category to '{current_status_category}' based on average.") # DEBUG PRINT


    def go_to_sensor_graph(self, instance):
        app = App.get_running_app()
        app.root.current = 'sensor_graph_screen' # Name of the screen holding CreatConnectUI

    def share_with_doctor(self, instance):
        print("Sharing with doctor (feature not implemented yet)")