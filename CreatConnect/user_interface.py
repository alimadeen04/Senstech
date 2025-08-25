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

import threading, numpy as np
from kivy.clock import Clock
from pstat_driver import run_cv_blocking
from calibration import Calibrator
from sensor_pipeline import concentration_from_cv
from personalization import get_status, get_breakdown
import sensor_input  # for load_health_info()

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
   
        # Initialize creatinine_label with placeholder text
        self.creatinine_label = Label(text="[b][color=000000]Creatinine: -- mg/dL[/color][/b]",
                                      markup=True, font_size='18sp', size_hint_y=None, height=50) 
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

    # === RUN POTENTIOSTAT (CV) ===
    def start_pstat_cv(self, port, params, curr_range="100uA", sample_period_ms=10):
        """Called by MenuScreen.start_read_sensor"""
        # Visual reset
        self.graph.clear()
        self.status_label.text = "[b][color=000000]Status:[/color][/b] [b]Running CV...[/b]"
        self.creatinine_label.text = "[b][color=000000]Creatinine: -- mg/dL [/color][/b]"

        self._cal = Calibrator("calibration.json")

        def worker():
            try:
                t, V, I = run_cv_blocking(
                    port=port,
                    params=params,
                    curr_range=curr_range,
                    sample_period_ms=sample_period_ms,
                    name="cyclic",
                    show_progress=True
                )
            except Exception as e:
                Clock.schedule_once(lambda dt: self._on_pstat_error(str(e)), 0)
                return

            Clock.schedule_once(lambda dt: self._on_pstat_done(t, V, I), 0)

        threading.Thread(target=worker, daemon=True).start()

    def _on_pstat_error(self, msg: str):
        self.status_label.text = f"[b][color=000000]Status:[/color][/b] [b][color=cc0000]Error[/color][/b]"
        self.creatinine_label.text = f"[b][color=000000]{msg}[/color][/b]"
        print("Potentiostat error:", msg)

    def _autoscale_graph(self, V_volts, I_uA):
        g = self.graph.graph
        vmin, vmax = float(np.min(V_volts)), float(np.max(V_volts))
        imin, imax = float(np.min(I_uA)), float(np.max(I_uA))
        if vmin == vmax: vmax = vmin + 1.0
        if imin == imax: imax = imin + 1.0
        padI = 0.05 * (imax - imin)
        g.xmin, g.xmax = vmin, vmax
        g.ymin, g.ymax = imin - padI, imax + padI

    def _on_pstat_done(self, t, V, I):
        # Ensure numpy arrays
        V = np.asarray(V, dtype=float)
        I = np.asarray(I, dtype=float)

        # Units: many APIs return Amps. Convert to µA if values are small.
        if np.nanmax(np.abs(I)) < 1e-3:
            I_uA = I * 1e6
        else:
            I_uA = I  # already in µA

        # Plot entire curve (V vs I)
        try:
            self._autoscale_graph(V, I_uA)
            self.graph.update_graph(V.tolist(), I_uA.tolist())
        except Exception as e:
            print("Plotting error:", e)

        # === Peak → concentration via your calibration (use REDUCTION peak) ===
        conc_mg_dL, Ip_uA, Vp_mV, peak_idx = concentration_from_cv(
            V, I_uA, self._cal, smooth_k=5, peak="reduction"
        )  # CHANGED: unpack 4 values

        if conc_mg_dL is None:
            self._on_pstat_error("No data captured.")
            return

        # Calibration debug printout (what value was used and how)
        # try:
            # dbg = self._cal.apply_debug(Ip_uA)
            # print(
                # f"[CAL DEBUG] peak_mode=reduction idx={peak_idx} "
                # f"I_raw={dbg['x_raw_uA']:.3f} uA I_used={dbg['x_used_uA']:.3f} uA "
                # f"offset={dbg['x_offset_uA']:.3f} uA denom={dbg['denom_uA'] if dbg['denom_uA'] is not None else '—'} uA "
                # f"model={dbg['y_model']:.6f} {dbg['y_model_unit']} → out={dbg['y_out']:.3f} {dbg['y_out_unit']}"
            # )
            # Safety warning if the reduction peak wasn't actually negative
            # if Ip_uA >= 0:
                # print(f"[WARN] Expected reduction peak to be negative, got {Ip_uA:.3f} uA at idx={peak_idx}")
        # except Exception as e:
            # print("Cal debug failed:", e)

        # Personalized status
        info = sensor_input.load_health_info()
        status = get_status(conc_mg_dL, info["age"], info["gender"], info["weight"])
        color = {"Low":"cc0000", "Normal":"00aa00", "High":"ff9900"}.get(status,"000000")

        self.status_label.text     = f"[b][color=000000]Status:[/color][/b] [b][color={color}]{status}[/color][/b]"
        self.creatinine_label.text = f"[b][color=000000]Creatinine: {conc_mg_dL:.2f} mg/dL[/color][/b]"

        # Save to app history
        app = App.get_running_app()
        if not hasattr(app, "all_creatinine_readings"):
            app.all_creatinine_readings = []
        app.all_creatinine_readings.append(float(conc_mg_dL))

        # Push updates back to Menu + History Log
        Clock.schedule_once(self._trigger_menu_status_update, 0.05)
        Clock.schedule_once(self._update_history_log, 0.10)

        # (Optional) Save a snapshot of the graph
        try:
            import os, datetime
            os.makedirs("history_logs", exist_ok=True)
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            self.graph.export_to_png(f"history_logs/CV_{ts}.png")
        except Exception as e:
            print("Could not export graph image:", e)

        # --- END CONSOLIDATED INITIALIZATION ---
        
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
            print("❌ Could not access ScreenManager")
