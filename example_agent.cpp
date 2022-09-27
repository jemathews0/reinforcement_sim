#include <zmq.hpp>
#include <string>
#include <iostream>

enum Commands {
    APPLY_FORCE,
    SET_STATE,
    NEW_STATE,
    ANIMATE
};

struct SetStateCommand{
    int32_t command = SET_STATE;
    float x;
    float xdot;
    float theta;
    float thetadot;
};

struct ApplyForceCommand{
    int32_t command = APPLY_FORCE;
    float u;
};

struct NewStateCommand{
    int32_t command = NEW_STATE;
    float x;
    float xdot;
    float theta;
    float thetadot;
};

struct AnimateCommand{
    int32_t command = ANIMATE;
    int32_t enabled;
};


int main ()
{
    //  Prepare our context and socket
    zmq::context_t context (1);
    zmq::socket_t socket (context, zmq::socket_type::req);
    socket.connect ("tcp://localhost:5555");

    bool animation_enabled = true;
    int count = 0;
    while (true){
        if (count % 1000 == 0 ){
            AnimateCommand cmd;
            animation_enabled = !animation_enabled;
            cmd.enabled = animation_enabled;

            // Copy the command object into a request message
            zmq::message_t request (sizeof(cmd));
            memcpy(request.data(), &cmd, sizeof(cmd));

            // Send the messasge
            socket.send(request, zmq::send_flags::none);
        }
        // Every 1000 timesteps, reset the pendulum and cart
        else if( count % 1000 == 1) {
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

        int32_t response_command = reinterpret_cast<int32_t*>(reply.data())[0];

        if (response_command == NEW_STATE) {
            NewStateCommand* newStateCmdPtr = reinterpret_cast<NewStateCommand*>(reply.data());

            float x = newStateCmdPtr->x;
            float xdot = newStateCmdPtr->xdot;
            float theta = newStateCmdPtr->theta;
            float thetadot = newStateCmdPtr->thetadot;

        }
        else if (response_command == ANIMATE) {
            AnimateCommand* animateCmdPtr = reinterpret_cast<AnimateCommand*>(reply.data());
            animation_enabled = animateCmdPtr->enabled;
        }
        else {
            std::cout << "Error: invalid command " << response_command << std::endl;
        }

    }
    return 0;
}
