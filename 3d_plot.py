import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

fig = plt.figure()
ax = Axes3D(fig)

entry = np.arange(1, 513)
share = np.arange(1, 65, 0.125)
entry, share = np.meshgrid(entry, share)


Z = 12 + np.log2(entry) + np.log(share)

ax.plot_surface(entry, share, Z, cmap='rainbow')
ax.contourf(entry, share, Z, zdir='z', offset=0, cmap='rainbow')

plt.show()