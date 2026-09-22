# COHERENT Migration

This repository preserves the original COHERENT Git history while tracking the
project's environment and middleware migration.

## Version lines

- `upstream-original`: original upstream baseline at commit
  `17554a52792e302921bbb5e5fd3b4049e25b50d4`.
- `ubuntu20-ros1`: verified fixes and portability changes made while reproducing
  the project on Ubuntu 20.04 with ROS1 Noetic.
- `ubuntu22-ros2`: ongoing migration to Ubuntu 22.04 and ROS2 Humble.

The original project is available at
<https://github.com/MrKeee/COHERENT>. The migration repository does not claim
ownership of the upstream project or its assets.

## Compatibility boundary

The migration intentionally keeps the authors' modified Isaac Sim 2022.2.0 and
the repository's modified OmniGibson 0.2.1. Upgrading either simulator is outside
the current migration scope.

ROS2 Humble uses system Python 3.10, while Isaac Sim 2022.2.0 embeds Python
3.7.13. They should remain in separate processes; ROS2's `rclpy` must not be
forced into the Isaac Python environment. A process bridge will be introduced
for action and result exchange.

## Files not stored in Git

Large datasets, robot assets, Isaac Sim installations, generated ROS build
trees, experiment logs, credentials, and machine-local configuration are
excluded. They must be restored separately according to their original licenses
and installation instructions.

## Migration order

1. Verify NVIDIA driver and Vulkan support on Ubuntu 22.04.
2. Restore and test the modified Isaac Sim 2022.2.0 installation.
3. Rebuild the pinned OmniGibson environment and restore external data/assets.
4. Validate simulator startup, scene loading, and each robot incrementally.
5. Build equivalent ROS2 message and test nodes with ROS2 Humble.
6. Add the Python 3.7 to Python 3.10 process bridge.
7. Validate one action, a fixed text plan, and finally PEFA integration.
