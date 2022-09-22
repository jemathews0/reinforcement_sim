#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 14 15:04:22 2021

@author: jonathan
"""
from scipy.integrate import solve_ivp
import matplotlib as mpl
import matplotlib.animation as anim
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
plt.rcParams['text.usetex'] = True


class SinglePendulumCart:
    def __init__(self, m1, m2, I2, l, w1, h1, w2, l2):
        self.m1 = m1
        self.m2 = m2
        self.I2 = I2
        self.l = l

        self.p1 = patches.Rectangle((-w1/2, -h1/2), w1, h1)
        self.p2 = patches.Rectangle((-w2/2, 0), w2, l2)

    def deriv(self, t, y, u, params):
        g = 9.81
        x = y[0]
        xdot = y[1]
        theta = y[2]
        thetadot = y[3]
        try:
            u = u[0]
        except IndexError:
            u = u

        A = np.array([[-(self.m1+self.m2), self.m2*self.l*np.cos(theta)],
                      [self.m2*self.l*np.cos(theta), -(self.m2*self.l**2+self.I2)]])
        b = np.array([[self.m2*self.l*np.sin(theta)*thetadot**2-u],
                      [-self.m2*self.l*np.sin(theta)*g]])

        xddot, thetaddot = np.linalg.solve(A, b)

        return np.array([xdot, xddot[0], thetadot, thetaddot[0]])

    def draw(self, ax, y):
        x = y[0]
        theta = y[2]

        t1 = mpl.transforms.Affine2D().translate(x, 0) + ax.transData
        t2 = mpl.transforms.Affine2D().rotate(
            theta) + mpl.transforms.Affine2D().translate(x, 0) + ax.transData
        self.p1.set_transform(t1)
        self.p2.set_transform(t2)
        return self.p1, self.p2

def get_u(state):
    return [0]

def main():
    u = 0
    m1 = 1
    m2 = 1
    L = 1
    I2 = 1/12*m2*L**2
    l = L/2
    w1 = 0.4
    h1 = 0.2
    w2 = 0.1
    l2 = L
    singlePendulumCart = SinglePendulumCart(m1, m2, I2, l, w1, h1, w2, l2)

    T = np.linspace(0, 10, 1001)
    timestep = T[1]-T[0]
    
    x = 0
    xdot = 0
    theta = 0.1
    thetadot = 0

    state = np.array([x, xdot, theta, thetadot])
    state_labels = [r'$x$', r'$\dot x$', r'$\theta$', r'$\dot \theta$']

    us = []
    states = []
    for t in T:
        u = get_u(state)
        us.append(u)
        res = solve_ivp(singlePendulumCart.deriv, [0, timestep], state, args=[u,0])
        state = res.y[:,-1]
        states.append(state)

    states = np.array(states).T
    print("states shape", states.shape)


    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_xlim(-5, 5)
    ax.set_ylim(-5, 5)
    plt.axis('equal')

    def init_patches():
        y = states[:, 0]
        patches = singlePendulumCart.draw(ax, y)
        for patch in patches:
            ax.add_patch(patch)
        return patches

    def animate(i):
        y = states[:, i]
        patches = singlePendulumCart.draw(ax, y)

        return patches

    animation = anim.FuncAnimation(
        fig, animate, init_func=init_patches, interval=(T[1]-T[0])*1000, frames=states.shape[1], repeat=False, blit=True)

    plt.figure()
    plt.xlabel('Time (s)')
    plt.plot(T, us, label=r'$u$')
    for i in range(len(state)):
        plt.plot(T, states[i], label=state_labels[i])
    plt.legend()


    plt.show()
    return animation


if __name__ == "__main__":
    animation = main()
