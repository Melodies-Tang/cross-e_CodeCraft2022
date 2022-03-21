import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


def draw(usage):
    fig = plt.figure()
    ax = Axes3D(fig)
    N = [i for i in range(len(usage))]
    T = [i for i in range(len(usage[0]))]
    ax.plot_surface()
    plt.show()

