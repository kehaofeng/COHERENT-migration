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
forced into the Isaac Python environment. The migration uses a loopback TCP/JSON
bridge for action and result exchange.

## Current issue and change ledger

| Observed problem | Root cause | Migration change | Verification |
| --- | --- | --- | --- |
| The original setup selected OpenCV 5.0 in 2026 | `opencv-python` had no version bound | Pin `opencv-python==4.7.0.72` in `OmniGibson/setup.py` | Installed metadata, import and OmniGibson startup verified |
| First Isaac/OmniGibson startup exited with code 137 | 15 GiB RAM was exhausted during RTX shader compilation and the system had no swap | Document an 8 GiB swap requirement for this test machine | Shader compilation completed; later empty-app startup took about 12 seconds |
| `agents` could not be imported | Required `COHERENT_PATH` was absent in the shell | Keep paths environment-driven; do not add a machine path to source | Empty OmniGibson app started, updated and shut down with exit code 0 |
| ROS1 code imported `rospy` inside Isaac's Python 3.7 process | Humble `rclpy` is built for Python 3.10 and is not ABI-compatible with Python 3.7 | Add `ros2_hademo_ws`, `hademo_nodes/sim_bridge.py`, and Python-3.7-compatible `ros2_transport.py` | Custom ROS2 Action reached a Python 3.7 fake simulator and Result returned successfully |
| ROS1 message name `Func_and_Args` failed ROS2 naming rules | ROS2 interface type files require UpperCamelCase names | Rename the ROS2 copy to `FuncAndArgs`; retain the original ROS1 workspace unchanged | `colcon build` and Python message imports pass |
| ROS2 launcher could leave child nodes after simulator failure | Stopping a launcher PID did not reliably stop its descendant Python processes | Run each service in its own session/process group and clean up by PGID | SIGINT timeout test leaves no simulator, bridge, or publisher process |
| Full Merom scene exits with PhysX CUDA error 700 / code 139 | Existing full-scene GPU/PhysX failure on the RTX 4060 Laptop 8 GB configuration | No simulator-capacity source changes retained; record as a hardware/runtime validation boundary | Reproduced before the ROS2 bridge connected; empty app and transport tests still pass |

Dependency snapshots are stored under `dependency-locks/`. They separate the
planning Conda environment, the Isaac/OmniGibson Conda environment, ROS2 Debian
packages, and ROS2 system-Python support packages.

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
5. ~~Build equivalent ROS2 message and test nodes with ROS2 Humble.~~
6. ~~Add and unit-test the Python 3.7 to Python 3.10 process bridge.~~
7. Validate one action on target-class hardware, a fixed text plan, and finally
   PEFA integration. This remains blocked on the current laptop by the recorded
   full-scene PhysX/CUDA failure.
