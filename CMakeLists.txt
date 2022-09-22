
project(inverted_pendulum_cpp)


find_package(cppzmq)

add_executable(inverted_pendulum_client_cpp inverted_pendulum_client.cpp)
target_link_libraries(inverted_pendulum_client_cpp cppzmq)

