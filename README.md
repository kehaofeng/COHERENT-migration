# COHERENT 复现与迁移

本仓库记录对 [MrKeee/COHERENT](https://github.com/MrKeee/COHERENT) 的学习性复现与环境迁移。

代码基线来自原项目提交 `17554a52792e302921bbb5e5fd3b4049e25b50d4`。原项目介绍、论文、安装说明和作者信息请以原项目仓库为准。

## 仓库版本

- `main`：带来源说明的原项目代码快照。
- `ubuntu20-ros1`：在 Ubuntu 20.04 和 ROS1 Noetic 上复现时验证过的修复。
- `ubuntu22-ros2`：迁移到 Ubuntu 22.04 和 ROS2 Humble 的版本。

迁移范围、兼容性限制、未纳入 Git 的外部数据以及迁移进度见迁移分支中的 [MIGRATION.md](MIGRATION.md)。

## 来源与版权说明

COHERENT 以及仓库中基于 OmniGibson 的代码来自各自的原作者。本仓库只记录下游修改，不声明拥有原项目。已有的版权和许可证文件均予以保留，下游修改可通过 Git 历史查看。

大型模拟器安装文件、数据集、机器人资源、生成的构建目录、密钥和实验日志不通过本仓库分发。
