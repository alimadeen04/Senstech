# graph.py
"""
graph.py - Handles graphing of historical creatinine levels.

- Real-time updating of the graph.
- Integration with stored historical data.
- Machine Learning-based predictions?
    - Predict future creatinine levels based on past data.
    - Identify anomalous readings based on user-specific trends.
    - Provide personalized alerts before a major health issue occurs.
"""

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
            ymin=-6.0,
            ymax=7.0,
            x_ticks_minor=1,     # one minor tick between each major
            x_ticks_major=0.1,
            y_ticks_major=1,
            y_grid_label=True,
            x_grid_label=True,
            padding=5,
            x_grid=True,
            y_grid=True,
            background_color=(1, 1, 1, 1),
            tick_color=(0, 0, 0, 1),
            label_options={'color': (0, 0, 0, 1), 'bold': True},
        )

        self.plot = LinePlot(line_width=1.5, color=[1, 0, 0, 1])
        self.graph.add_plot(self.plot)
        self.add_widget(self.graph)

        # buffers for fast incremental updates
        self._x, self._y = [], []

    def update_graph(self, x_vals, y_vals):
        # optional: guard for mismatched lengths
        n = min(len(x_vals), len(y_vals))
        self._x = list(x_vals[:n])
        self._y = list(y_vals[:n])
        self.plot.points = list(zip(self._x, self._y))

    def append_point(self, x, y):
        self._x.append(x)
        self._y.append(y)
        self.plot.points = list(zip(self._x, self._y))

    def clear(self):
        self._x, self._y = [], []
        self.plot.points = []

    def set_limits(self, xmin, xmax, ymin, ymax, pad_y_frac=0.05):
        self.graph.xmin, self.graph.xmax = float(xmin), float(xmax)
        pad = pad_y_frac * (ymax - ymin)
        self.graph.ymin, self.graph.ymax = float(ymin) - pad, float(ymax) + pad


     
