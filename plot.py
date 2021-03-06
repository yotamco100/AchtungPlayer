import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.cbook as cbook
import time
import numpy as np

fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)

def animate(i):
    fname = cbook.get_sample_data('C:\\Users\\User\\Desktop\\byle\'s achtung project\\Trial2 - Keras\\plot1.csv', asfileobj=False)

    # test 2; use names
    pullData = open('..\\Trial2 - Keras\\plot1.csv', 'r').read()
    dataArray = pullData.split('\n')
    xar = []
    yar = []
    for line in dataArray[1:]:
        if len(line) > 1:
            x,y = line.split(',')
            xar.append(int(x))
            yar.append(float(y))
    ax1.clear()
    ax1.plot(xar,yar)

ani = animation.FuncAnimation(fig,animate,interval=1000)
plt.show()
