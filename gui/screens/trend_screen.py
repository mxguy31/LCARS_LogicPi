from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.lang.builder import Builder
from kivy.properties import (DictProperty, NumericProperty, ListProperty)
from kivy.utils import rgba
from kivy.clock import Clock

from datetime import timedelta, datetime
from gui.widgets.time_graph import TimeSeriesGraph
from gui.widgets.graph import MeshLinePlot
from gui.constants import GUI_CONST
import time

Builder.load_file(str(GUI_CONST.SCREEN_DIR.joinpath('trend_screen.kv')))


class TrendScreen(Screen):    
    data_list = DictProperty({})
    data_selection = ListProperty([])
    
    label0 = ListProperty(['', rgba('#33CC99')])
    label1 = ListProperty(['', rgba('#CC4499')])
    label2 = ListProperty(['', rgba('#CC33FF')])
    label3 = ListProperty(['', rgba('#FF7700')])
    label4 = ListProperty(['', rgba('#FFCC33')])
    label5 = ListProperty(['', rgba('#88CCFF')])
    
    x_v1 = NumericProperty()
    x_v2 = NumericProperty()
    y_v1 = NumericProperty()
    y_v2 = NumericProperty()
    
    max_x = NumericProperty(168)  # Hours in 7 days
    min_x = NumericProperty(0)
    max_y = NumericProperty(100)
    min_y = NumericProperty(0)

    def __init__(self, **kw):
        super().__init__(**kw)
        self.app = App.get_running_app()
        self.db = self.app.database
        self.plots = dict()
        self.graph_view = None
        self.bind(data_selection=self.update_plot_selection)
        
        self.bind(x_v1=self.update_graph_view,
                  x_v2=self.update_graph_view,
                  y_v1=self.update_graph_view,
                  y_v2=self.update_graph_view)
        
        Clock.schedule_once(self.after_init, 0)
        self.update_clock = Clock.schedule_interval(self.update_data, 1)
        self.update_clock.cancel()  # Just create the clock, don't run it

    def after_init(self, *args):
        x_values = list(range(self.max_x + 1))
        current_datetime = datetime.now().replace(microsecond=0)
        current_datetime += timedelta(hours=1)
        major_period = timedelta(hours=1)
        date_values = [current_datetime - major_period * i for i in x_values]
        self.graph_view = TimeSeriesGraph(date_values,
                                        date_label_format='%b-%d %H:00',
                                        x_grid_label=True,
                                        y_grid_label=True,
                                        x_grid=True,
                                        y_grid=True,
                                        font_size='12sp',
                                        label_options={'font_name': 'LCARS_Bold'})
        self.viewgrid.add_widget(self.graph_view)
        self.update_graph_view()
            
    def on_pre_enter(self):
        self.data_list = self.db.data_read()
        self.update_clock()

    def on_pre_leave(self):
        self.update_clock.cancel()

    def update_plot_selection(self, *args):
        remove_list = list()
        label_list = (self.label0, self.label1, self.label2,
                          self.label3, self.label4, self.label5)
        for plot in self.plots.keys():
            if plot not in self.data_selection:
                self.graph_view.remove_plot(self.plots[plot])
                remove_list.append(plot)

        for plot in remove_list:
            self.plots.pop(plot, None)
            for label in label_list:
                if label[0] == plot:
                    label[0] = ''

        for data_point in self.data_selection[:6]:
            if data_point not in self.plots:
                for label in label_list:
                    if label[0] == '':
                        label[0] = data_point
                        break
                self.plots[data_point] = MeshLinePlot(color=label[1])
                self.graph_view.add_plot(self.plots[data_point])
        
        self.update_data()
        

    def update_graph_view(self, *args):
        if not self.graph_view:
            return

        x_diff = self.x_v2 - self.x_v1
        if x_diff < 10:
            self.graph_view.x_ticks_major = 1
            self.graph_view.x_ticks_minor = 0
        elif x_diff < 30:
            self.graph_view.x_ticks_major = 3
            self.graph_view.x_ticks_minor = 3
        elif x_diff < 60:
            self.graph_view.x_ticks_major = 6
            self.graph_view.x_ticks_minor = 6
        elif x_diff < 120:
            self.graph_view.x_ticks_major = 12
            self.graph_view.x_ticks_minor = 4
        elif x_diff < 240:
            self.graph_view.x_ticks_major = 24
            self.graph_view.x_ticks_minor = 4
        elif x_diff < 480:
            self.graph_view.x_ticks_major = 48
            self.graph_view.x_ticks_minor = 4
        else:
            self.graph_view.x_ticks_major = 168
            self.graph_view.x_ticks_minor = 7
        
        y_diff = self.y_v2 - self.y_v1
        if y_diff < 10:
            self.graph_view.y_ticks_major = 1
            self.graph_view.y_ticks_minor = 4
        elif y_diff < 25:
            self.graph_view.y_ticks_major = 2
            self.graph_view.y_ticks_minor = 4
        elif y_diff < 50:
            self.graph_view.y_ticks_major = 5
            self.graph_view.y_ticks_minor = 5
        elif y_diff < 100:
            self.graph_view.y_ticks_major = 10
            self.graph_view.y_ticks_minor = 5
        elif y_diff < 150:
            self.graph_view.y_ticks_major = 10
            self.graph_view.y_ticks_minor = 0
        else:
            self.graph_view.y_ticks_major = 20
            self.graph_view.y_ticks_minor = 0
        
        self.graph_view.xmin = self.x_v1
        self.graph_view.xmax = self.x_v2
        self.graph_view.ymin = self.y_v1
        self.graph_view.ymax = self.y_v2

    def update_data(self, *args):
        high_y = 1
        low_y = 65535
        unix_now = int(time.time())
        for plot in self.plots.keys():
            n_entries = list()
            entries = self.db.get_datalog_entries(plot)
            if entries is None:
                entries = [(0,0)]

            for i in range(len(entries)):
                (x, y) = entries[i]
                x = (unix_now - x) / 3600  # hours since now
                if x > self.max_x:
                    break

                points = [(x, y)]

                if isinstance(y, bool):
                    nt_y = int(not y)
                    y = int(y)
                    if len(entries) > 1:
                        points = [(x - 0.0001, y), (x, nt_y)]

                high_y = y if y >= high_y else high_y
                low_y = y if y <= low_y else low_y
                
                n_entries.extend(points)

            if len(n_entries) == 0:
                n_entries = [(0, 0)]
                low_y = 0
                high_y = 0
            first_y = n_entries[0][1]
            n_entries.insert(0, (0, first_y))
            self.plots[plot].points = n_entries

        if len(self.plots) > 0:
            low_y = 0 if low_y < 2 else low_y
            high_y = 2 if high_y < 2 else high_y
            self.min_y = round(low_y * 0.75)
            self.max_y = round(high_y * 1.25)
        else:
            self.min_y = 0
            self.max_y = 100

        self.update_graph_view()
