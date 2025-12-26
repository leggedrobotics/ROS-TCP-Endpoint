from vr_haptic_msgs.msg import ManoLandmarks 
from ..publisher import RosPublisher
from .registry import register_publisher
from geometry_msgs.msg import Point
from rclpy.serialization import deserialize_message
import struct
import numpy as np

def decode_custom_mano_packet(data: bytes):
    """
    Decodes a packet that matches ROS1 std_msgs/Header + Point[] layout:

      [u32 seq][u32 stamp.secs][u32 stamp.nsecs]          # 12 bytes (ROS1 Header part)
      [u32 frame_id_len][frame_id bytes]                 # ROS1 string
      [u32 N]                                            # array length
      [N * (float64 x,y,z)]                              # geometry_msgs/Point[] as doubles

    Returns a ManoLandmarks ROS2 message.

    Args:
      data: bytes buffer
      ManoLandmarks: ROS2 message class (callable to construct)
      Point: geometry_msgs.msg.Point class (optional but recommended)
      use_numpy: if True, uses numpy.frombuffer if numpy is available
    """
    mv = memoryview(data)
    off = 0

    # ---- header: seq, stamp.secs, stamp.nsecs (12 bytes) ----
    if len(mv) < 12 + 4 + 4:
        raise ValueError(f"Packet too small: {len(mv)} bytes")

    seq, secs, nsecs = struct.unpack_from("<III", mv, off)
    off += 12

    # ---- frame_id string ----
    (frame_len,) = struct.unpack_from("<I", mv, off)
    off += 4

    if len(mv) < off + frame_len + 4:
        raise ValueError(f"Packet too small for frame_id ({frame_len} bytes) and N")

    frame_id = bytes(mv[off:off + frame_len]).decode("utf-8", errors="replace")
    off += frame_len

    # ---- number of points ----
    (n,) = struct.unpack_from("<I", mv, off)
    off += 4

    expected = n * 24  # N * (3 * float64)
    remaining = len(mv) - off
    if remaining != expected:
        raise ValueError(
            f"Invalid payload size: n={n}, remaining={remaining}, expected={expected} "
            f"(total={len(mv)}, off={off})"
        )

    msg = ManoLandmarks()
    # fill ROS2 header (seq doesn't exist in ROS2 Header)
    msg.header.stamp.sec = int(secs)
    msg.header.stamp.nanosec = int(nsecs)
    msg.header.frame_id = frame_id
    # ---- landmarks ----
    # Fast path: numpy (if available)
    arr = np.frombuffer(mv, dtype="<f8", offset=off, count=n * 3).reshape(n, 3)
    msg.landmarks = [Point(x=float(x), y=float(y), z=float(z)) for x, y, z in arr]
    return msg

@register_publisher(ManoLandmarks)
class HandPosePublisher(RosPublisher):
    """
    Publisher for hand pose data
    """

    def __init__(self, topic, queue_size=10):
        if ManoLandmarks is None:
            raise ImportError("vr_haptic_msgs package is not available.")
        super().__init__(topic, ManoLandmarks, queue_size)
        
        self._is_ros2_compatible = True

    def send(self, data):
        """
        Publishes hand pose data to the specified ROS topic.

        Args:
            data: The serialized ManoLandmarks message data coming from outside of ROS

        Returns:
            None
        """
        if self._is_ros2_compatible:
            try:
                message_type = type(self.msg)
                message = deserialize_message(data, message_type)
                self.pub.publish(message)
            except Exception as e:
                self.get_logger().error(f"Failed to deserialize ROS2 message: {e} Retrying with custom decoder.")
                self._is_ros2_compatible = False

        if not self._is_ros2_compatible:
            try:
                message = decode_custom_mano_packet(data)
                self.pub.publish(message)
            except Exception as e:
                self.get_logger().error(f"Failed to decode custom ManoLandmarks packet: {e}")
        return None