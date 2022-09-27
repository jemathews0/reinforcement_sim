#!/usr/bin/env python3

from scipy.integrate import solve_ivp
import inverted_pendulum as ip
import json
import matplotlib.animation as anim
import matplotlib.pyplot as plt
import numpy as np
import struct
import zmq


def main():
    APPLY_FORCE = 0
    SET_STATE = 1
    NEW_STATE = 2
    ANIMATE = 3

    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5555")

    animation_enabled = True
    count = 0
    while True:
        if count % 1000 == 0:

            # toggle animation
            command = ANIMATE
            animation_enabled = not animation_enabled
            request_bytes = struct.pack('ii', command, animation_enabled)
            socket.send(request_bytes)

        elif count % 1000 == 1:
            # reset the state
            command = SET_STATE
            x = -2.0
            xdot = 0.0
            theta = 0.2
            thetadot = 0.0
            request_bytes = struct.pack(
                'iffff', command, x, xdot, theta, thetadot)
            socket.send(request_bytes)

        else:
            command = APPLY_FORCE
            u = 0.1
            request_bytes = struct.pack('if', command, u)
            socket.send(request_bytes)

        count += 1

        response_bytes = socket.recv()
        response_command, = struct.unpack('i', response_bytes[0:4])

        if response_command == NEW_STATE:
            x, xdot, theta, thetadot = struct.unpack(
                'ffff', response_bytes[4:])
            new_state = [x, xdot, theta, thetadot]
        elif response_command == ANIMATE:
            animation_enabled, = struct.unpack('i', response_bytes[4:])
        else:
            print("Error: invalid command: ", response_command)


if __name__ == "__main__":
    main()
