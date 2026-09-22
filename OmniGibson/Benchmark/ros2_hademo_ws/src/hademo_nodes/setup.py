from setuptools import find_packages, setup


package_name = "hademo_nodes"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="COHERENT migration maintainers",
    maintainer_email="kehaofeng@todo.invalid",
    description="ROS 2 bridge nodes for COHERENT.",
    license="MIT",
    entry_points={
        "console_scripts": [
            "action_publisher = hademo_nodes.action_publisher:main",
            "sim_bridge = hademo_nodes.sim_bridge:main",
        ],
    },
)
