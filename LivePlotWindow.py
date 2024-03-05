from PyQt5.QtWidgets import QWidget, QVBoxLayout
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar


class LivePlotWindow(QWidget):
    def __init__(self, measurement):
        super().__init__()

        # Default Figure Setting
        self.xs = None
        self.ys = None

        self._measurement = measurement
        self.x_axis_label = measurement.get_x_axis_label()
        self.y_axis_label = measurement.get_y_axis_label()

        self._init_draw()  # create sub-plots and call FuncAnimation()
        self._init_ui()
        self.show()

    def __del__(self):
        plt.close()

    # override figure close event from QWidget
    def close_event(self, event):
        self.close()

    def _init_ui(self):
        vbox = QVBoxLayout()
        vbox.addWidget(self.toolbar)
        vbox.addWidget(self.canvas)
        self.setLayout(vbox)
        # self.setGeometry(400, 300, 400, 600)

    def _init_draw(self):
        # for PyQt embedding
        self.fig = plt.Figure()
        self.axis = self.fig.add_subplot()
        self.canvas = FigureCanvas(self.fig)
        self.toolbar = NavigationToolbar(self.canvas, self)

        self.axis.set_ylabel(self.y_axis_label)
        self.axis.set_xlabel(self.x_axis_label)
        self.axis.clear()

        self.ani = animation.FuncAnimation(fig=self.fig,
                                           func=self.animate,
                                           interval=10,
                                           blit=False,
                                           save_count=100)
        self.canvas.draw()

    def _before_drawing(self):
        if self._measurement.all_data_drawn():
            self.ani.event_source.stop()
            self.close()
        else:
            raw_data = self._measurement.get_data_point()
            self.xs = raw_data[0]
            self.ys = raw_data[1]

    def animate(self, event):
        self._before_drawing()  # update data

        self.axis.grid(True)
        if self.xs is not None and self.ys is not None:
            self.axis.plot(self.xs, self.ys, 'ro')

    def pause(self):
        # self.ani.event_source.stop()
        self.ani.pause()

    def resume(self):
        # self.ani.event_source.start()
        self.ani.resume()

    def close(self):
        self.ani.event_source.stop()
        super().close()
