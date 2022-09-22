#!/usr/bin/env python3

from scipy.integrate import solve_ivp
import inverted_pendulum as ip
import json
import matplotlib.animation as anim
import matplotlib.pyplot as plt
import numpy as np
import zmq

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
    singlePendulumCart = ip.SinglePendulumCart(m1, m2, I2, l, w1, h1, w2, l2)

    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5555")

    vis = Visualizer(singlePendulumCart)

    timestep = 0.01

    animation = anim.FuncAnimation(
            vis.fig,  vis.animate, producer(singlePendulumCart, socket, timestep), vis.init_patches, interval=timestep*1000, blit=True)

    plt.show()
    return animation, context, socket

def advance_one_step(pend_cart, u, state, timestep):
    res = solve_ivp(pend_cart.deriv, [0, timestep], state, args=[[u],0])
    new_state = res.y[:,-1]

    return new_state

def get_reward(state, u, new_state):
    if new_state[2] > np.pi/2 or new_state[2] < -np.pi/2:
        return -1
    else:
        return 0


def producer(pend_cart, socket, timestep):
    response_dict = {}
    state = [0.,0.,0.2,0.]
    yield state
    while True:
        command, message_str = socket.recv_multipart()
        message_dict = json.loads(message_str.decode())
        print("received: {} : {}".format(command, message_str))


        if command == b'do_action':
            u = message_dict["control_input"]
            new_state = advance_one_step(pend_cart, u, state, timestep)
            reward = get_reward(state, u, new_state)

            response_dict["new_state"] = list(new_state)
            response_dict["reward"] = reward

            response_str = json.dumps(response_dict).encode()

            socket.send_multipart([b"response", response_str])

            state = new_state
        elif command == b'set_state':
            state = message_dict["state"]
            socket.send_multipart([b"response", b"{}"])

        yield state

class Visualizer():
    def __init__(self, pend_cart):

        self.pend_cart = pend_cart

        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlim(-5, 5)
        self.ax.set_ylim(-5, 5)
        plt.axis('equal')

    def init_patches(self):
        y = [0,0,0,0]
        patches = self.pend_cart.draw(self.ax, y)
        for patch in patches:
            self.ax.add_patch(patch)
        return patches

    def animate(self, state):
        patches = self.pend_cart.draw(self.ax, state)

        return patches



if __name__ == "__main__":
    animation, context, socket = main()
