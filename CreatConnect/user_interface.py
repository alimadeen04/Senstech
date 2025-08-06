'''
user_interface.py - sensor graph screen UI
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
        
        self.status_label = Label(text="[b][color=000000]Status:[/color][/b] [b][color=00aa00] [/color][/b]",
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


        # Graph (inside its own StyleCard)
        graph_card = StyleCard(size_hint=(1, 1)) # Graph takes remaining vertical space
        self.graph = CreatinineGraph(size_hint=(1,1))
        graph_card.add_widget(self.graph)
        self.add_widget(graph_card)

        # --- CONSOLIDATED GRAPH DATA TRACKING INITIALIZATION ---
        self.readings = []
        self.timestamps = []
        self.start_time = time.time()

        # Attributes for Data
        self.simulated_df = None
        self.sim_index = 0
        self.sim_total_steps = 120
        self.sim_timer = None

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
        from sensor_input import read_simulated_sensor_data
        print("🔄 Reading sensor...")
        sim_result = read_simulated_sensor_data()
        self.simulated_df = sim_result["data"]
        print(f"📂 File: {sim_result['file']}")
        print(f"🧪 Creatinine: {sim_result['creatinine']} ({sim_result['status']})")

        # Extract full CV data
        voltages = list(self.simulated_df["Voltage (V)"])
        currents = list(self.simulated_df["Current (μA)"])
        self.graph.update_graph(voltages, currents)  # 🔴 Plot entire curve immediately

        # Use the simulated creatinine value
        creatinine_val = sim_result["creatinine"]
        self.creatinine_label.text = f"[b][color=000000]Creatinine: {creatinine_val:.2f} mg/dL[/color][/b]"

        # Set status color and label
        if creatinine_val < 0.6:
            color = "cc0000"
            status = "Low"
        elif creatinine_val <= 1.3:
            color = "00aa00"
            status = "Normal"
        else:
            color = "ff9900"
            status = "High"

        self.status_label.text = f"[b][color=000000]Status:[/color][/b] [b][color={color}]{status}[/color][/b]"

        # Save reading to history
        app = App.get_running_app()
        if app is not None:
            if not hasattr(app, 'all_creatinine_readings'):
                app.all_creatinine_readings = []
            app.all_creatinine_readings.append(creatinine_val)
            print("✅ Sensor reading complete and graph updated.")



    # def _plot_next_sim_point(self, dt):
        # if self.sim_index >= self.sim_total_steps:
            # Clock.unschedule(self.sim_timer)
           # self.sim_timer = None
            # self._finalize_sensor_reading()
           #  return

        # voltage = self.sim_df.iloc[self.sim_index]["Voltage (V)"]
        # current = self.simulated_df.iloc[self.sim_index]["Current (μA)"]

        # self.timestamps.append(voltage)
        # self.readings.append(current)

        # self.graph.update_graph(self.timestamps, self.readings)
        # self.sim_index += 1

    def _finalize_sensor_reading(self):
        peak_value = max(self.readings)
        self.creatinine_label.text = f"[b][color=000000]Creatinine: {peak_value:.2f} mg/dL[/color][/b]"

        if peak_value < 0.6:
            color = "cc0000"
            status = "Low"
        elif peak_value <= 1.3:
            color = "00aa00"
            status = "Normal"
        else:
            color = "ff9900"
            status = "High"

        self.status_label.text = f"[b][color=000000]Status:[/color][/b] [b][color={color}]{status}[/color][/b]"

        # Save data for syncing - append to existing readings
        app = App.get_running_app()
        if not hasattr(app, 'all_creatinine_readings'):
            app.all_creatinine_readings = []
        app.all_creatinine_readings.append(peak_value)
        
        # Debug print to verify readings are being accumulated
        print(f"✅ _finalize_sensor_reading - Added reading: {peak_value:.2f} mg/dL")
        print(f"✅ _finalize_sensor_reading - Total readings in history: {len(app.all_creatinine_readings)}")
        print(f"✅ _finalize_sensor_reading - All readings: {app.all_creatinine_readings}")

        def delayed_screen_switch(dt):
            print("✅ Reading completed - staying on current screen")
            # Update menu status without switching screens
            Clock.schedule_once(self._trigger_menu_status_update, 0.2)

        Clock.schedule_once(delayed_screen_switch, 0.5)

    # def start_real_time_plotting(self, dt):
        # app = App.get_running_app()
        # self.readings = []
        # self.timestamps = []
        # self.start_time = time.time()
        # self.sim_index = 0
        # self.sim_df = app.simulated_df
        # self.sim_timer = Clock.schedule_interval(self.plot_next_point, 1)

    def plot_next_point(self, dt):
        if self.sim_index >= len(self.sim_df):
            Clock.unschedule(self.sim_timer)
            self.finish_plotting()
            return

        raw_val = self.sim_df.iloc[self.sim_index]["Current (μA)"]
        creatinine = raw_val * 1.75

        self.readings.append(creatinine)
        self.timestamps.append(self.sim_index)

        self.graph.update_graph(self.timestamps, self.readings)
        self.sim_index += 1

    def finish_plotting(self):
        app = App.get_running_app()
        peak_val = max(self.readings)

        if peak_val < 0.6:
            color = "cc0000"
            status = "Low"
        elif peak_val <= 1.3:
            color = "00aa00"
            status = "Normal"
        else:
            color = "ff9900"
            status = "High"

        # Update Sensor Graph screen
        self.status_label.text = f"[b][color=000000]Status:[/color][/b] [b][color={color}]{status}[/color][/b]"
        self.creatinine_label.text = f"[b][color=000000]Creatinine: {peak_val:.2f} mg/dL[/color][/b]"

        # Save graph image
        filename = f"{app.simulated_file}_graph.png"
        self.graph.export_to_png(f"history_logs/{filename}")

        # Store final value - append to existing readings
        if not hasattr(app, 'all_creatinine_readings'):
            app.all_creatinine_readings = []
        app.all_creatinine_readings.append(peak_val)
        
        # Debug print to verify readings are being accumulated
        print(f"✅ Added reading: {peak_val:.2f} mg/dL")
        print(f"✅ Total readings in history: {len(app.all_creatinine_readings)}")
        print(f"✅ All readings: {app.all_creatinine_readings}")

        def switch_and_update(dt):
            print("✅ Reading completed - staying on current screen")
            # Update menu status and history log without switching screens
            Clock.schedule_once(self._trigger_menu_status_update, 0.2)
            # Update history log if it exists
            Clock.schedule_once(self._update_history_log, 0.3)

        Clock.schedule_once(switch_and_update, 0.5) 

       
    def _trigger_menu_status_update(self, dt):
        app = App.get_running_app()
        sm = app.root

        if sm and hasattr(sm, 'get_screen'):
            menu_screen = sm.get_screen('menu_screen')
            if hasattr(menu_screen, 'children') and len(menu_screen.children) > 0:
                menu_widget = menu_screen.children[0]
                if hasattr(menu_widget, 'update_menu_status'):
                    print("✅ Calling update_menu_status()")
                    menu_widget.update_menu_status()
                else:
                    print("❌ menu_widget has no method update_menu_status")
            else:
                print("❌ menu_screen.children is empty or missing")
        else:
            print("❌ Could not access ScreenManager")

    def _update_history_log(self, dt):
        """Update history log screen with new reading"""
        app = App.get_running_app()
        sm = app.root

        if sm and hasattr(sm, 'get_screen'):
            try:
                history_screen = sm.get_screen('history_log_screen')
                if hasattr(history_screen, 'children') and len(history_screen.children) > 0:
                    history_widget = history_screen.children[0]
                    if hasattr(history_widget, 'load_history'):
                        print("✅ Updating history log with new reading")
                        history_widget.load_history()
                    else:
                        print("❌ history_widget has no method load_history")
                else:
                    print("❌ history_screen.children is empty or missing")
            except Exception as e:
                print(f"❌ Error updating history log: {e}")
        else:
            print("❌ Could not access ScreenManager for history log update")











       

       


       