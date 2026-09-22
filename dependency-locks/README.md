# 依赖版本快照

COHERENT 使用三套刻意隔离的运行环境。不要把这些软件包列表合并安装到同一个 Python 环境中。

| 环境层 | Python | 关键版本 | 快照文件 |
| --- | --- | --- | --- |
| 规划模块 | Conda 3.10.21 | NumPy 1.26.4、PyYAML 6.0.3、OpenAI 3.17.0 | `coherent-pip.txt` |
| 模拟器 | Conda 3.7.13 + Isaac runtime | OmniGibson 0.2.1、OpenCV 4.7.0.72、NumPy 1.21.6 | `omnigibson-pip.txt` |
| ROS2 | Ubuntu 系统 Python 3.10.12 | ROS2 Humble、ros-base 0.10.0 | `ros2-humble-deb.txt` |
| ROS2 Python 支持包 | Ubuntu 系统 Python 3.10.12 | NumPy 1.21.5、SciPy 1.8.0、PyYAML 5.4.1 | `ros2-system-python-deb.txt` |

Isaac Sim 2022.2.0 还提供了一些不在 Conda 软件包元数据中的运行模块，包括 PyTorch 1.13.0+cu117、torchvision 0.14.0+cu117 和 Warp 0.6.1，因此这些版本不会出现在 `omnigibson-pip.txt` 中。

项目需要 NVIDIA 显卡和 CUDA。当前使用 NVIDIA 驱动 580.178.04；Isaac Sim 自带 CUDA 运行库，因此没有另外安装 CUDA Toolkit。

这些文件记录的是已经验证过的 Ubuntu 22.04 环境，不要直接把所有包升级到最新版。

只有在有意修改依赖后才重新生成快照：

```bash
python -m pip list --format=freeze | LC_ALL=C sort
dpkg-query -W -f='${Package}==${Version}\n' 'ros-humble-*' ros-dev-tools ros2-apt-source
```
