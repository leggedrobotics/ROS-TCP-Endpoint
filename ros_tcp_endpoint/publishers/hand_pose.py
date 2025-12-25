from vr_haptic_msgs.msg import ManoLandmarks 
from ..publisher import RosPublisher
from .registry import register_publisher
from geometry_msgs.msg import Point

import struct

def decode_custom_mano_packet(data: bytes, ManoLandmarks, Point=None):
    """
    Decodes:
      [12 bytes header][u32 len][frame_id][u32 N][N*(double x,y,z)]
    into a ManoLandmarks ROS2 message.

    If landmarks is geometry_msgs/Point[], pass Point=geometry_msgs.msg.Point.
    """
    off = 0
    if len(data) < 12 + 4 + 4:
        raise ValueError(f"Packet too small: {len(data)} bytes")

    # 12-byte custom header (unknown); keep it or parse if you know what it is
    off += 12

    frame_len = struct.unpack_from("<I", data, off)[0]; off += 4
    frame_id = data[off:off+frame_len].decode("utf-8", errors="replace"); off += frame_len

    n = struct.unpack_from("<I", data, off)[0]; off += 4

    expected = n * 24
    remaining = len(data) - off
    if remaining != expected:
        raise ValueError(f"Expected {expected} bytes for {n} doubles-triplets, got {remaining}")

    msg = ManoLandmarks()
    msg.header.frame_id = frame_id

    # If your message uses geometry_msgs/Point[]:
    if Point is not None:
        for _ in range(n):
            x, y, z = struct.unpack_from("<ddd", data, off); off += 24
            msg.landmarks.append(Point(x=float(x), y=float(y), z=float(z)))
        return msg

    # Otherwise: adapt to your landmark element type here
    # (e.g., element has fields x,y,z or .position.x/.position.y/.position.z)
    raise RuntimeError("Pass Point=geometry_msgs.msg.Point or adapt landmark element assignment.")

@register_publisher(ManoLandmarks)
class HandPosePublisher(RosPublisher):
    """
    Publisher for hand pose data
    """

    def __init__(self, topic, queue_size=10):
        if ManoLandmarks is None:
            raise ImportError("vr_haptic_msgs package is not available.")
        super().__init__(topic, ManoLandmarks, queue_size)

    def send(self, data):
        """
        Publishes hand pose data to the specified ROS topic.

        Args:
            data: The serialized ManoLandmarks message data coming from outside of ROS

        Returns:
            None
        """

        msg = decode_custom_mano_packet(data, ManoLandmarks, Point=Point)
        self.pub.publish(msg)

        return None