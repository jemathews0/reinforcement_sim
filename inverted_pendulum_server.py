#!/usr/bin/env python3

from scipy.integrate import solve_ivp
import argparse
import inverted_pendulum as ip
import json
import matplotlib.animation as anim
import matplotlib.pyplot as plt
import numpy as np
import struct
import zmq


def main(args):
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
    singlePendulumCart = ip.SinglePendulumCart(m1, m2, I2, l, w1, h1, w2, l2)

    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5555")

    timestep = 0.01

    prod = producer(singlePendulumCart, socket, timestep, args)

    vis = Visualizer(singlePendulumCart)
    animation = anim.FuncAnimation(
        vis.fig,  vis.animate, prod, vis.init_patches, interval=timestep*1000, blit=True)

    plt.show()
    return animation, context, socket


def advance_one_step(pend_cart, u, state, timestep):
    res = solve_ivp(pend_cart.deriv, [0, timestep], state, args=[[u], 0])
    new_state = res.y[:, -1]

    return new_state


def get_reward(state, u, new_state):
    if new_state[2] > np.pi/2 or new_state[2] < -np.pi/2:
        return -1
    else:
        return 0


def producer(pend_cart, socket, timestep, args):
    APPLY_FORCE = 0
    SET_STATE = 1
    NEW_STATE = 2
    ANIMATE = 3

    response_dict = {}
    state = [0., 0., 0.2, 0.]
    yield state
    while True:
        message_bytes = socket.recv()
        command, = struct.unpack('i', message_bytes[0:4])

        if command == APPLY_FORCE:
            u, = struct.unpack('f', message_bytes[4:])
            new_state = advance_one_step(pend_cart, u, state, timestep)

            response_bytes = struct.pack('iffff', NEW_STATE, *new_state)
            socket.send(response_bytes)

            state = new_state
        elif command == SET_STATE:
            x, xdot, theta, thetadot = struct.unpack('ffff', message_bytes[4:])
            new_state = [x, xdot, theta, thetadot]


            response_bytes = struct.pack('iffff', NEW_STATE, *new_state)
            socket.send(response_bytes)

            state = new_state
        elif command == ANIMATE:
            enabled, = struct.unpack('i', message_bytes[4:])
            args.animate = enabled

            response_bytes = struct.pack('ii', ANIMATE, args.animate)
            socket.send(response_bytes)
        else:
            print("Error: invalid command: ", command)

        if args.animate:
            yield state
        else:
            print(state)


class Visualizer():
    def __init__(self, pend_cart):

        self.pend_cart = pend_cart

        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlim(-5, 5)
        self.ax.set_ylim(-5, 5)
        plt.axis('equal')

    def init_patches(self):
        y = [0, 0, 0, 0]
        patches = self.pend_cart.draw(self.ax, y)
        for patch in patches:
            self.ax.add_patch(patch)
        return patches

    def animate(self, state):
        patches = self.pend_cart.draw(self.ax, state)

        return patches


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulate an inverted pendulum")
    parser.add_argument('--animate', action='store_true')
    args = parser.parse_args()
    animation, context, socket = main(args)
