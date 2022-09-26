# Installation

## Python server and example agent

Create a virtual environment to house dependencies for this project. This makes
it easy to remove all the dependencies later as the virtual environment can
just be deleted.

```
python3 -m venv /path/to/env
```

Activate the environment. You'll need to do this every time you open your terminal back up.

```
source /path/to/env/bin/activate
```

Install the python dependencies.

```
pip install -r requirements.txt
```

## C++ example agent

Follow the [cppzmq installation
instructions.](https://github.com/zeromq/cppzmq#build-instructions) then build
the example agent as follows:

```
mkdir build
cd build
cmake ..
make
```

# Running

You will need to start the server and a single agent in two separate terminals
so they are both running at the same time. Also, if one dies you will have to
close and restart the other one as well or it won't reconnect.

## Inverted pendulum server

To run the server with animation of the pendulum enabled

```
./inverted_pendulum_server.py --animate
```

To run as fast as possible, omit the animate argument

## Python example agent

```
./example_agent.py
```

## C++ example agent

If you've made changes to the agent, recompile it:

```
cd build
make
cd ..
```

Then run the agent with this command:

```
./build/example_agent_cpp
```

