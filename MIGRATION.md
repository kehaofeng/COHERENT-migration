# COHERENT 迁移说明

本仓库在保留 COHERENT 原项目来源记录的同时，跟踪环境和中间件迁移过程。

## 版本分支

- `upstream-original`：原项目基线，提交号为 `17554a52792e302921bbb5e5fd3b4049e25b50d4`。
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
- NVIDIA 驱动 580.178.04（当前测试电脑）

项目需要 NVIDIA 显卡和 CUDA。Isaac Sim 已经带有运行所需的 CUDA 库，当前环境没有另外安装 CUDA Toolkit。

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

## 测试结果

- OmniGibson 可以启动、更新并正常关闭。
- ROS2 工作区可以成功编译。
- ROS2 消息可以传给 Python 3.7 测试程序，结果也可以返回。
- 启动脚本退出后没有遗留 ROS2 和模拟器进程。
- 当前电脑是 RTX 4060 Laptop 8GB。完整 Merom 场景会因为显存不足出现 CUDA error 700，所以完整机器人动作需要在显存更大的电脑上继续测试。

## 没有放进 GitHub 的内容

- Isaac Sim 安装目录
- 大型数据集和机器人资源
- Conda 环境目录
- API Key
- 构建文件和实验日志

这些内容需要在新电脑上单独安装或复制。
