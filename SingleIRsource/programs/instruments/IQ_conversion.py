#function to correct IQ and convert them from IQ signals to amplitude and frequency

import numpy as np
# pip install lsq-ellipse
from ellipse import LsqEllipse
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse

def ellipse_fit(I, Q, plot=False, run = 1):
    X = np.array(list(zip(I, Q)))
    reg = LsqEllipse().fit(X)
    center, width, height, phi = reg.as_parameters()
    # center = coordinates of ellipse center
    # width  = Total length (diameter) of horizontal axis (a, the largest)
    # height = Total length (diameter) of vertical axis (b, the smallest)
    # angle  = Rotation in degrees anti-clockwise (radians)

    # print(f'center: {center[0]:.3f}, {center[1]:.3f}')
    # print(f'width: {width:.3f}')
    # print(f'height: {height:.3f}')
    # print(f'phi: {phi:.3f}')

    if plot:
        fig = plt.figure(figsize=(6, 6))
        ax = plt.subplot()
        ax.axis('equal')
        ax.plot(I ,Q, 'ro', zorder=1)
        ellipse = Ellipse(
            xy=center, width=2*width, height=2*height, angle=np.rad2deg(phi),
            edgecolor='b', fc='None', lw=2, label='Fit', zorder=2
        )
        ax.add_patch(ellipse)

        plt.xlabel('I')
        plt.ylabel('Q')

        plt.legend()
        plt.savefig('IQfit_ellipse' + str(run) + '.png') 
    
    return reg