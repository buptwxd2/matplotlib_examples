import numpy as np
import matplotlib.pyplot as plt

n = 256

entry = np.linspace(1, 512, n)
share = np.linspace(1, 64, n)
entry, share = np.meshgrid(entry, share)


Z = 12 + np.log2(entry) + np.log(share)

plt.contour(entry, share, Z, 10, colors='black', linewidth=.5)
plt.contourf(entry, share, Z, 10, alpha=0.5, cmap='rainbow')

plt.show()
