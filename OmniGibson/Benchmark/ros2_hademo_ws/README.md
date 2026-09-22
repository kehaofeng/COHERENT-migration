# COHERENT ROS2 工作区

这是 Ubuntu 22.04 / ROS2 Humble 使用的工作区。原来的 ROS1 工作区没有删除，可以用来对照。

Isaac Sim 使用 Python 3.7，ROS2 Humble 使用 Python 3.10，所以增加了一个 bridge，让两个环境可以互相传递动作和结果。

## 第一次准备

先安装 Isaac Sim 2022.2.0、Miniconda 和 ROS2 Humble，然后进入项目目录：

```bash
cd /你的路径/COHERENT
export COHERENT_PATH="$PWD"
source ~/miniconda3/etc/profile.d/conda.sh
cd OmniGibson
./scripts/setup.sh
```

运行 `setup.sh` 时，按照提示输入 Isaac Sim 2022.2.0 的安装路径，并使用默认环境名 `omnigibson`。

## 构建

```bash
cd /你的路径/COHERENT
export COHERENT_PATH="$PWD"
sudo rosdep init                 # 每台机器只需执行一次
rosdep update                    # 首次执行，之后按需更新索引
cd "$COHERENT_PATH/OmniGibson/Benchmark/ros2_hademo_ws"
rosdep install --from-paths src --ignore-src -r -y
./build.sh
```

如果 `rosdep update` 因网络超时失败，可以等网络恢复后再运行。

## 运行

```bash
cd "$COHERENT_PATH/OmniGibson/Benchmark"
./run_ros2.sh Merom_1_int_Task1
```

脚本会自动启动 OmniGibson、ROS2 bridge 和动作发布节点。按 `Ctrl+C` 可以停止。

bridge 默认使用 `127.0.0.1:8765`。

## 当前验证范围

- ROS2 接口和节点已通过 `colcon build`。
- ROS2 Action 可以传到 Python 3.7 测试程序，Result 也可以正常返回。
- 启动脚本退出后不会遗留模拟器、bridge 或动作发布节点。
- 完整 Merom 场景仍需在显存充足的目标机器上完成最终动作验收。
