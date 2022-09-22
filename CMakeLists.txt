
project(inverted_pendulum_cpp)


find_package(cppzmq)

add_executable(example_agent_cpp example_agent.cpp)
target_link_libraries(example_agent_cpp cppzmq)

