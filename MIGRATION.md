# COHERENT 迁移说明


## 版本分支

- `upstream-original`：原项目基线。
- `ubuntu20-ros1`：在 Ubuntu 20.04 和 ROS1 Noetic 上复现时验证过的修复与路径兼容改动。
- `ubuntu22-ros2`：迁移到 Ubuntu 22.04 和 ROS2 Humble 的版本。

原项目地址：<https://github.com/MrKeee/COHERENT>。本迁移仓库不声明拥有原项目或其资源。

## 环境版本

- Ubuntu 22.04
- ROS2 Humble
- Miniconda
- 规划环境：Python 3.10.21
- 模拟器环境：Python 3.7.13
- Isaac Sim 2022.2.0
- OmniGibson 0.2.1
- OpenCV 4.7.0.72
- PyTorch 1.13.0+cu117

更完整的软件包列表放在 `dependency-locks/` 中。

## 修改内容

1. 修复了代码中的作者电脑绝对路径，改用 `COHERENT_PATH` 和 `ISAAC_PATH`。
2. 将 OpenCV 固定为 4.7.0.72，避免自动安装到 OpenCV 5。
3. 保留原 ROS1 工作区，另外新增 ROS2 Humble 工作区。
4. 将 ROS1 自定义消息改成 ROS2 消息，其中 `Func_and_Args.msg` 改名为 `FuncAndArgs.msg`。
5. 新增 ROS2 bridge，让 ROS2 的 Python 3.10 可以和 Isaac Sim 的 Python 3.7 通信。
6. 修改 `sim.py`，让模拟器通过 bridge 接收动作并返回结果。
7. 新增 `run_ros2.sh`，用于一起启动模拟器、bridge 和动作发布节点。
8. 增加依赖版本记录，方便在其他电脑重新安装。


## 没有放进 GitHub 的内容

- Isaac Sim 安装目录
- 大型数据集和机器人资源
- Conda 环境目录
- API Key
- 构建文件和实验日志
