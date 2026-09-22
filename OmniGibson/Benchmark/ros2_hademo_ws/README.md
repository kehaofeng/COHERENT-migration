# COHERENT ROS 2 workspace

This workspace is the Ubuntu 22.04 / ROS 2 Humble counterpart of the original
`ros_hademo_ws` ROS 1 workspace. The ROS 1 workspace is retained as a reference.

Isaac Sim 2022.2.0 embeds Python 3.7, while ROS 2 Humble provides `rclpy` for
Python 3.10. They therefore run in separate processes. `hademo_nodes/sim_bridge`
converts ROS 2 messages to newline-delimited JSON over a loopback-only TCP
connection; `Benchmark/ros2_transport.py` receives them inside OmniGibson.

## Build

```bash
sudo rosdep init                 # once per machine
rosdep update                    # once, then whenever indexes need updating
cd "$COHERENT_PATH/OmniGibson/Benchmark/ros2_hademo_ws"
rosdep install --from-paths src --ignore-src -r -y
./build.sh
```

## Run

```bash
cd "$COHERENT_PATH/OmniGibson/Benchmark"
./run_ros2.sh Merom_1_int_Task1
```

The bridge defaults to `127.0.0.1:8765`. Override it with
`COHERENT_BRIDGE_HOST` and `COHERENT_BRIDGE_PORT` when needed. Do not expose the
port to another network unless transport authentication is added first.
