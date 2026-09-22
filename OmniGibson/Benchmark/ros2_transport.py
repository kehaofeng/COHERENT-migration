"""Python 3.7-compatible transport between OmniGibson and the ROS 2 bridge."""

import json
import os
import socket
import threading

import numpy as np


class SocketActionTransport:
    """Expose the small interface that ``sim.py`` used from the ROS 1 helper.

    Isaac Sim 2022.2.0 embeds Python 3.7, while ROS 2 Humble's rclpy extension
    targets Python 3.10.  A loopback TCP connection keeps those ABIs in
    separate processes.  Messages are newline-delimited JSON objects.
    """

    def __init__(self, task_name):
        self.task_name = task_name
        self._next_step_action = None
        self._lock = threading.Lock()
        self._send_lock = threading.Lock()
        self._connection = None

        host = os.getenv("COHERENT_BRIDGE_HOST", "127.0.0.1")
        port = int(os.getenv("COHERENT_BRIDGE_PORT", "8765"))
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server.bind((host, port))
        self._server.listen(1)

        print("Simulation waits for the ROS 2 bridge at {}:{}".format(host, port))
        self._connection, address = self._server.accept()
        print("ROS 2 bridge connected from {}:{}".format(*address))
        self._reader = self._connection.makefile("r")
        self._reader_thread = threading.Thread(target=self._receive_loop, daemon=True)
        self._reader_thread.start()
        self._send({"type": "ready", "task_name": task_name})

    @property
    def next_step_action(self):
        with self._lock:
            return self._next_step_action

    def _receive_loop(self):
        try:
            for line in self._reader:
                message = json.loads(line)
                if message.get("type") == "action":
                    action = message["action"]
                    for command in action.values():
                        if len(command) < 2:
                            continue
                        arguments = command[1]
                        if "waypoint_pos" in arguments:
                            arguments["waypoint_pos"] = np.asarray(
                                arguments["waypoint_pos"], dtype=np.float64
                            ).reshape(-1, 3)
                        if "waypoint_ori" in arguments:
                            arguments["waypoint_ori"] = np.asarray(
                                arguments["waypoint_ori"], dtype=np.float64
                            ).reshape(-1, 4)
                    with self._lock:
                        self._next_step_action = action
        except (OSError, ValueError) as error:
            print("ROS 2 bridge connection stopped: {}".format(error))

    def _send(self, message):
        payload = (json.dumps(message, separators=(",", ":")) + "\n").encode("utf-8")
        with self._send_lock:
            self._connection.sendall(payload)

    def publish_feedback_result(self, feedback_result):
        # The ROS 1 implementation published an empty Result message too; keep
        # that behavior until detailed skill feedback is defined by the project.
        with self._lock:
            self._next_step_action = None
        self._send({"type": "result"})

    def close(self):
        if self._connection is not None:
            self._connection.close()
        self._server.close()
