# https://github.com/Chao-Jen/garden.graph
# Modified the example (simplified) as it wouldn't run under recent kivy
# versions. The keyword 'month' would break the requirements for the
# x_ticks_major property as it only accepts an int value. 
# Removed the example as the imports caused issues
# bound to date labels to allow updates on time changes

from gui.widgets.graph import (Graph, identity, exp10, log10)
from kivy.graphics.transformation import Matrix
from kivy.properties import ListProperty
from math import radians


class TimeSeriesGraph(Graph):
    x_date_labels = ListProperty()

    def __init__(self, x_date_labels, date_label_format='%b', _with_stencilbuffer=False, **kwargs):
        self.x_date_labels = x_date_labels
        self._date_label_format = date_label_format
        self._with_stencilbuffer = _with_stencilbuffer
        kwargs["xmin"] = 0
        kwargs["xmax"] = len(self.x_date_labels) - 1
        self.bind(x_date_labels=self._redraw_all)
        super(TimeSeriesGraph, self).__init__(**kwargs)

    def _get_ticks(self, major, minor, log, s_min, s_max):
        if major == 'month':
            points_major = []
            m = self.x_date_labels[0].month
            for i in range(len(self.x_date_labels)):
                if self.x_date_labels[i].month != m:
                    m = self.x_date_labels[i].month
                    points_major.append(float(i))

            points_minor = []
        else:
            points_major, points_minor = super(TimeSeriesGraph, self)._get_ticks(major, minor, log, s_min, s_max)

        return points_major, points_minor

    def _update_labels(self, *args):
        xlabel = self._xlabel
        ylabel = self._ylabel
        x = self.x
        y = self.y
        width = self.width
        height = self.height
        padding = self.padding
        x_next = padding + x
        y_next = padding + y
        xextent = width + x
        yextent = height + y
        ymin = self.ymin
        ymax = self.ymax
        xmin = self.xmin
        precision = self.precision
        x_overlap = False
        y_overlap = False
        # set up x and y axis labels
        if xlabel:
            xlabel.text = self.xlabel
            xlabel.texture_update()
            xlabel.size = xlabel.texture_size
            xlabel.pos = int(x + width / 2. - xlabel.width / 2.), int(padding + y)
            y_next += padding + xlabel.height
        if ylabel:
            ylabel.text = self.ylabel
            ylabel.texture_update()
            ylabel.size = ylabel.texture_size
            ylabel.x = padding + x - (ylabel.width / 2. - ylabel.height / 2.)
            x_next += padding + ylabel.height
        xpoints = self._ticks_majorx
        xlabels = self._x_grid_label
        xlabel_grid = self.x_grid_label
        ylabel_grid = self.y_grid_label
        ypoints = self._ticks_majory
        ylabels = self._y_grid_label
        # now x and y tick mark labels
        if len(ylabels) and ylabel_grid:
            # horizontal size of the largest tick label, to have enough room
            funcexp = exp10 if self.ylog else identity
            funclog = log10 if self.ylog else identity
            ylabels[0].text = precision % funcexp(ypoints[0])
            ylabels[0].texture_update()
            y1 = ylabels[0].texture_size
            y_start = y_next + (padding + y1[1] if len(xlabels) and xlabel_grid
                                else 0) + \
                               (padding + y1[1] if not y_next else 0)
            yextent = y + height - padding - y1[1] / 2.

            ymin = funclog(ymin)
            ratio = (yextent - y_start) / float(funclog(ymax) - ymin)
            y_start -= y1[1] / 2.
            y1 = y1[0]
            for k in range(len(ylabels)):
                ylabels[k].text = precision % funcexp(ypoints[k])
                ylabels[k].texture_update()
                ylabels[k].size = ylabels[k].texture_size
                y1 = max(y1, ylabels[k].texture_size[0])
                ylabels[k].pos = tuple(map(int, (x_next, y_start +
                                                 (ypoints[k] - ymin) * ratio)))
            if len(ylabels) > 1 and ylabels[0].top > ylabels[1].y:
                y_overlap = True
            else:
                x_next += y1 + padding
        if len(xlabels) and xlabel_grid:
            funcexp = exp10 if self.xlog else identity
            funclog = log10 if self.xlog else identity
            # find the distance from the end that'll fit the last tick label
            xlabels[0].text = precision % funcexp(xpoints[-1])
            xlabels[0].texture_update()
            xextent = x + width - xlabels[0].texture_size[0] / 2. - padding
            # find the distance from the start that'll fit the first tick label
            if not x_next:
                xlabels[0].text = precision % funcexp(xpoints[0])
                xlabels[0].texture_update()
                x_next = padding + xlabels[0].texture_size[0] / 2.
            xmin = funclog(xmin)
            ratio = (xextent - x_next) / float(funclog(self.xmax) - xmin)
            right = -1
            for k in range(len(xlabels)):
                xlabels[k].text = self.x_date_labels[int(xpoints[k])].strftime(self._date_label_format)
                # update the size so we can center the labels on ticks
                xlabels[k].texture_update()
                xlabels[k].size = xlabels[k].texture_size
                xlabels[k].pos = tuple(map(int, (x_next + (xpoints[k] - xmin)
                    * ratio - xlabels[k].texture_size[0] / 2., y_next)))
                if xlabels[k].x < right:
                    x_overlap = True
                    break
                right = xlabels[k].right
            if not x_overlap:
                y_next += padding + xlabels[0].texture_size[1]
        # now re-center the x and y axis labels
        if xlabel:
            xlabel.x = int(x_next + (xextent - x_next) / 2. - xlabel.width / 2.)
        if ylabel:
            ylabel.y = int(y_next + (yextent - y_next) / 2. - ylabel.height / 2.)
            t = Matrix().translate(ylabel.center[0], ylabel.center[1], 0)
            t = t.multiply(Matrix().rotate(-radians(270), 0, 0, 1))
            ylabel.transform = t.multiply(
                Matrix().translate(
                    -int(ylabel.center_x),
                    -int(ylabel.center_y),
                    0))
        if x_overlap:
            for k in range(len(xlabels)):
                xlabels[k].text = ''
        if y_overlap:
            for k in range(len(ylabels)):
                ylabels[k].text = ''
        return x_next - x, y_next - y, xextent - x, yextent - y
