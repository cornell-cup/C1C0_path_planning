import random
from collections import deque
import time
import math
from marvelmind import MarvelmindHedge

import numpy as np
import matplotlib.pyplot as plt

def visualize_old():

    k = 10
    plt.ion()
    xs = []
    ys = []

    xs = deque([0] * (k - len(xs)) + xs)
    ys = deque([0] * (k - len(ys)) + ys)

    colors = np.linspace(0,10,k)

    s = plt.scatter(xs, ys, c=colors, cmap="Blues")
    plt.show()

    axes = plt.gca()
    axes.set_xlim([-5,5])
    axes.set_ylim([-5,5])
    plt.pause(0.5)

    with open('out.csv', 'r') as file:
        for i, line in enumerate(file):
            if 880 <= i < 1170:
                print(i, line)
                x, y = float(line[0:line.index(",")]), float(line[line.index(",")+1:-1])
                plt.pause(0.1)
                xs.append(x)
                ys.append(y)
                if len(xs) > k:
                    xs.popleft()
                    ys.popleft()
                s.set_offsets(np.c_[xs,ys])
                plt.show()

    cont = True

    while cont:
        cont = input(">") not in ["quit", "exit", "done"]

def visualize_live():
    plt.ion()
    k = 50
    logging = False
    x = MarvelmindHedge()
    x.start()
    time.sleep(1)
    start_time = time.time()
    xs = []
    ys = []
    xs = deque([0] * (k - len(xs)) + xs)
    ys = deque([0] * (k - len(ys)) + ys)

    axes = plt.gca()
    axes.set_xlim([-5, 5])
    axes.set_ylim([-5, 5])
    colors = np.linspace(0, 10, k)
    s = plt.scatter(xs, ys, c=colors, cmap="Blues")
    plt.show()

    i = 0
    while time.time() - start_time < 20:
        plt.pause(0.1)
        time.sleep(0.01)
        t = x.position()
        xs.append(t[1])
        ys.append(t[2])
        print(i, xs[-1], ys[-1])
        i += 1
        if len(xs) > k:
            xs.popleft()
            ys.popleft()
        s.set_offsets(np.c_[xs, ys])
        plt.show()

    x.stop()
    print(math.sqrt((xs[-1] - xs[0]) ** 2 + (ys[-1] - ys[0]) ** 2) * 3.28084)

    cont = True
    while cont:
        cont = input(">") not in ["quit", "exit", "done"]

visualize_live()
