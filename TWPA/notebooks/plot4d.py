import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

F = F*1e-9

G_max = max(maxima)
best_V, best_P, best_F = amax(maxima)
best_V = V[best_V]
best_P = P[best_P]
best_F = F[best_f]

fig, ax = plt.subplots()
plt.subplots_adjust(bottom=0.25)


ax_volt = plt.axes(V)

svolt = Slider(
    ax_volt, "Bias Voltage (V)", v0, v1,
    valinit=v0, valstep=dv,
    initcolor='none'  # Remove the line marking the valinit position.
)

def update(val):
    volt = svolt.val
	volt_index = np.round((volt - v0)/dv)
	ax.colormesh(P, F, maxima[volt_index][:][:], vmin = min(maxima), vmax = G_max)
	fig.xlabel("Pump power (dBm)")
	fig.ylabel("Pump frequency (GHz)")
	fig.colorbar(label = "Power (dBm)")
    fig.canvas.draw_idle()


svolt.on_changed(update)

plt.show()