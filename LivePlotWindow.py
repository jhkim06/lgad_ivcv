from PyQt5.QtWidgets import QWidget, QVBoxLayout
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar


class LivePlotWindow(QWidget):
    def __init__(self, measurement):
        super().__init__()

        # Default Figure Setting
        self._number_of_figures = 1
        self.xs = list()
        self.ys = list()

        self._measurement = measurement

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
        self.canvas = FigureCanvas(self.fig)
        self.toolbar = NavigationToolbar(self.canvas, self)

        # make figure list
        self._plots = list()
        for idx in range(0, self._number_of_figures):
            # able to draw n row 1 col fig
            self._plots.append({"FIGURE": self.fig.add_subplot(self._number_of_figures, 1, idx + 1),
                                'INDEX': list()})
            self._plots[idx]['FIGURE'].clear()

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

        for item in self._plots:
            # item['FIGURE'].clear()
            item['FIGURE'].grid(True)
            if self.xs is not None and self.ys is not None:
                item['FIGURE'].plot(self.xs, self.ys, 'ro')

    def pause(self):
        # self.ani.event_source.stop()
        self.ani.pause()

    def resume(self):
        # self.ani.event_source.start()
        self.ani.resume()

    def close(self):
        self.ani.event_source.stop()
        super().close()
