#!/usr/bin/env python3

from scipy.integrate import solve_ivp
import inverted_pendulum as ip
import json
import matplotlib.animation as anim
import matplotlib.pyplot as plt
import numpy as np
import zmq

def main():
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5555")

    command = b'do_action'
    request_dict = {"control_input":0.0}
    while True:
        request_str = json.dumps(request_dict).encode()
        socket.send_multipart([command, request_str])

        resp_command, response_str = socket.recv_multipart()
        print("response: ", response_str)


if __name__ == "__main__":
    main()
