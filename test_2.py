import numpy as np
from matplotlib import animation as ani
from matplotlib import pyplot as plt
import threading
import time
from drivers.liveplot import FuncAnimationDisposable
import matplotlib
matplotlib.use('Qt5Agg')
# WebAgg
# TkAgg with error


n = 10
nPI = n * np.pi
fig, ax = plt.subplots()
arr = []
t = np.arange(0.0, nPI, 0.1)


def get_data():
	if len(arr) == len(t):
		return None
	else:
		return arr


def measure(return_sweep=True):
	global n, nPI, t
	arr.clear()
	nPI = n * np.pi
	t = np.arange(0.0, nPI, 0.1)
	if return_sweep:
		t = np.concatenate((t, t[-2::-1]))

	for ti in t:
		arr.append([ti, np.sin(ti) + np.random.normal(0, 0.05)])
		print("x: ", ti, " sin(x)", np.sin(ti))
		time.sleep(0.1)


def measurement_thread(init_value=0, final_value=10, return_sweep=True):
	global n
	n = final_value
	thread_1 = threading.Thread(target=measure, args=(return_sweep,))
	thread_1.start()


def show_plot(fig_=None, axs_=None):
	print(matplotlib.get_backend())
	if axs_ is not None:
		ax = axs_
	points, = ax.plot([], [], 'o', color='black')


	def init():
		points.set_data([], [])
		return points,

	def animate(frame, arr):
		# print("time", ti, " length", len(arr))
		# arr.append([ti, np.sin(ti)])
		arr_t = np.array(arr).T
		points.set_data(arr_t[0], arr_t[1])
		ax.relim()
		ax.autoscale()

		# Check if it's the last frame
		if len(arr) == len(t):
			# Signal that the animation has finished
			raise StopIteration
			print("Press q to continue")

		return points,

# def show_plot():
	# plt.close()
	measurement_thread()

	if fig_ is not None:
		fig = fig_

	ani_ = FuncAnimationDisposable(fig,
								   animate,
								   frames=None,
								   fargs=(arr,),
								   init_func=init,
								   blit=False,
								   repeat=False,
								   auto_close=True)
	fig.show()
	print('after show')

	# other_tasks()
	# open new window


def other_tasks():
	# Additional tasks after drawing all points
	print("Performing other tasks after drawing all points")
	print("Printing arr:")
	print(np.array(arr).T)


if __name__ == '__main__':
	show_plot()