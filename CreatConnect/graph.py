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

class CreatinineGraph(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.graph = Graph(
            xlabel='Voltage (V)',
            ylabel='Current (μA)',
            xmin=0.0,
            xmax=1.0,
            ymin = -6.0,
            ymax = 7.0,
            x_ticks_minor=1,
            x_ticks_major=0.1,
            y_ticks_major=1,
            y_grid_label=True,
            x_grid_label=True,
            padding=5,
            x_grid=True,
            y_grid=True,
            background_color=(1,1,1,1),
            tick_color=(0,0,0,1),
            label_options={'color': (0,0,0,1), 'bold': True}
        )

        self.plot = LinePlot(line_width=1.5, color=[1, 0, 0, 1])  # ✅ Make sure this line exists
        self.graph.add_plot(self.plot)
        self.add_widget(self.graph)


    def update_graph(self, x_vals, y_vals):
        self.plot.points = list(zip(x_vals, y_vals))

    def clear(self):
        self.plot.points = []

     
