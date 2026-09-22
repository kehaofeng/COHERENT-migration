import json
import os
import socket
import threading
import time

import rclpy
from hademo.msg import Action, Result
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, HistoryPolicy, QoSProfile, ReliabilityPolicy


AGENT_FIELDS = (
    "franka_0",
    "franka_1",
    "franka_2",
    "aliengo_0",
    "aliengo_1",
    "aliengo_2",
    "quadrotor_0",
    "quadrotor_1",
    "quadrotor_2",
)


def action_to_dict(message):
    action = {}
    for agent_name in AGENT_FIELDS:
        command = getattr(message, agent_name)
        decoded = []
        if command.has_func:
            decoded.append(command.func_name)
            if command.args.has_args:
                arguments = {"agent_name": agent_name}
                if "attached_prim" in command.func_name or "door_open" in command.func_name:
                    arguments["attached_prim_path"] = command.args.attached_prim_path
                else:
                    arguments.update(
                        waypoint_pos=list(command.args.waypoint_pos.data),
                        waypoint_ori=list(command.args.waypoint_ori.data),
                        waypoint_ind=command.args.waypoint_ind,
                    )
                    if "pick" in command.func_name:
                        arguments["attached_prim_path"] = command.args.attached_prim_path
            else:
                arguments = {"agent_name": agent_name}
            decoded.append(arguments)
        action[agent_name] = decoded
    return action


class SimulationBridge(Node):
    def __init__(self):
        super().__init__("coherent_sim_bridge")
        qos = QoSProfile(
            history=HistoryPolicy.KEEP_LAST,
            depth=10,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
        )
        self._result_publisher = self.create_publisher(Result, "resultTopic", qos)
        self._action_subscription = self.create_subscription(Action, "actionTopic", self._on_action, qos)
        self._socket = None
        self._send_lock = threading.Lock()
        self._connected = threading.Event()
        threading.Thread(target=self._connection_loop, daemon=True).start()

    def _connection_loop(self):
        host = os.getenv("COHERENT_BRIDGE_HOST", "127.0.0.1")
        port = int(os.getenv("COHERENT_BRIDGE_PORT", "8765"))
        attempts = 0
        while rclpy.ok():
            try:
                connection = socket.create_connection((host, port), timeout=2.0)
                connection.settimeout(None)
                self._socket = connection
                self._connected.set()
                self.get_logger().info("Connected to OmniGibson at %s:%d" % (host, port))
                with connection.makefile("r") as reader:
                    for line in reader:
                        message = json.loads(line)
                        if message.get("type") in ("ready", "result"):
                            self._result_publisher.publish(Result())
                if rclpy.ok():
                    self.get_logger().warning("OmniGibson connection closed; retrying")
            except (ConnectionError, OSError, ValueError) as error:
                attempts += 1
                if rclpy.ok() and (attempts == 1 or attempts % 10 == 0):
                    self.get_logger().info("Waiting for OmniGibson: %s" % error)
            finally:
                self._connected.clear()
                self._socket = None
            if rclpy.ok():
                time.sleep(1.0)

    def _on_action(self, message):
        if not self._connected.is_set():
            self.get_logger().warning("Dropping action because OmniGibson is not connected")
            return
        payload = json.dumps(
            {"type": "action", "action": action_to_dict(message)}, separators=(",", ":")
        ) + "\n"
        try:
            with self._send_lock:
                self._socket.sendall(payload.encode("utf-8"))
        except OSError as error:
            self.get_logger().error("Failed to forward action: %s" % error)


def main(args=None):
    rclpy.init(args=args)
    node = SimulationBridge()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
