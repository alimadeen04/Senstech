'''
graph.py - Handles graphing of historical creatinine levels.

- Real-time updating of the graph.
- Integration with stored historical data.
- Machine Learning-based predictions?
    - Predict future creatinine levels based on past data.
    - Identify anomalous readings based on user-specific trends.
    - Provide personalized alerts before a major health issue occurs.
'''

from kivy_garden.graph import Graph, LinePlot
from kivy.uix.boxlayout import BoxLayout
import time

class CreatinineGraph(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.graph = Graph(
            xlabel='Time (s)',
            ylabel='Creatinine (mg/dL)',
            x_ticks_minor=5,
            x_ticks_major=10,
            y_ticks_major=0.5,
            y_grid_label=True,
            x_grid_label=True,
            padding=5,
            x_grid=True,
            y_grid=True,
            xmin=0,
            xmax=60,
            ymin=0.0,
            ymax=3.0,
            background_color = (1,1,1,1),
            tick_color = (0,0,0,1),
            label_options = {'color': (0,0,0,1), 'bold': True}
        )
        self.plot = LinePlot(line_width=1.5, color=[1, 0, 0, 1])
        self.graph.add_plot(self.plot)
        self.add_widget(self.graph)
        

    def update_graph(self, x_vals, y_vals):
        self.plot.points = list(zip(x_vals, y_vals))