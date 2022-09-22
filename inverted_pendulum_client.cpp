#include <zmq.hpp>
#include <string>
#include <iostream>

enum Commands {
    APPLY_FORCE,
    SET_STATE,
    NEW_STATE
};

struct SetStateCommand{
    int command = SET_STATE;
    float x;
    float xdot;
    float theta;
    float thetadot;
};

struct ApplyForceCommand{
    int command = APPLY_FORCE;
    float u;
};

struct NewStateCommand{
    int command = NEW_STATE;
    float x;
    float xdot;
    float theta;
    float thetadot;
};


int main ()
{
    //  Prepare our context and socket
    zmq::context_t context (1);
    zmq::socket_t socket (context, zmq::socket_type::req);
    socket.connect ("tcp://localhost:5555");

    int count = 0;
    while (true){
        // Every 1000 timesteps, reset the pendulum and cart
        if( count % 1000 == 0) {
            // Create and populate a command object
            SetStateCommand cmd;
            cmd.x = -2;
            cmd.xdot = 0;
            cmd.theta = 0.2;
            cmd.thetadot = 0;

            // Copy the command object into a request message
            zmq::message_t request (sizeof(cmd));
            memcpy(request.data(), &cmd, sizeof(cmd));

            // Send the messasge
            socket.send(request, zmq::send_flags::none);
        }
        // Push right with a force of 0.1
        else {
            // Create and populate a command object
            ApplyForceCommand cmd;
            cmd.u = 0.1;
            zmq::message_t request (sizeof(cmd));
            memcpy(request.data(), &cmd, sizeof(cmd));
            socket.send(request, zmq::send_flags::none);
        }
        count++;

        zmq::message_t reply;
        zmq::recv_result_t res = socket.recv(reply, zmq::recv_flags::none);

        int response_command = reinterpret_cast<int32_t*>(reply.data())[0];

        if (response_command == NEW_STATE) {
            float* data = &(reinterpret_cast<float*>(reply.data())[1]);
            float x = data[0];
            float xdot = data[1];
            float theta = data[2];
            float thetadot = data[3];
        }
        else {
            std::cout << "Error: invalid command " << response_command << std::endl;
        }

    }
    return 0;
}
