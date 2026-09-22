# Dependency snapshots

COHERENT uses three deliberately separate runtime layers. Do not merge their
package lists into one Python environment.

| Layer | Python | Key versions | Snapshot |
| --- | --- | --- | --- |
| Planning | Conda 3.10.21 | NumPy 1.26.4, PyYAML 6.0.3, OpenAI 3.17.0 | `coherent-pip.txt` |
| Simulation | Conda 3.7.13 + Isaac runtime | OmniGibson 0.2.1, OpenCV 4.7.0.72, NumPy 1.21.6 | `omnigibson-pip.txt` |
| ROS 2 | Ubuntu system Python 3.10.12 | ROS 2 Humble, ros-base 0.10.0 | `ros2-humble-deb.txt` |
| ROS 2 Python support | Ubuntu system Python 3.10.12 | NumPy 1.21.5, SciPy 1.8.0, PyYAML 5.4.1 | `ros2-system-python-deb.txt` |

Isaac Sim 2022.2.0 supplies additional runtime modules outside Conda's package
metadata, including PyTorch 1.13.0+cu117, torchvision 0.14.0+cu117 and Warp
0.6.1. Those versions therefore do not appear in `omnigibson-pip.txt`.

The files are records of the verified Ubuntu 22.04 machine, not instructions to
upgrade every dependency. In particular, Isaac Sim's bundled packages have
known historical metadata conflicts; blindly upgrading them can break binary
compatibility.

Regenerate the snapshots after an intentional dependency change:

```bash
python -m pip list --format=freeze | LC_ALL=C sort
dpkg-query -W -f='${Package}==${Version}\n' 'ros-humble-*' ros-dev-tools ros2-apt-source
```
