"""
Publishers module for ROS-TCP-Endpoint.
"""

from .registry import (
    PUBLISHERS,
    register_publisher,
    get_publisher,
    list_topics,
)

try:
    from .hand_pose import HandPosePublisher
except ImportError:
    print("vr_haptic_msgs package is not available. HandPosePublisher will not be registered.")
    HandPosePublisher = None

__all__ = [
    'PUBLISHERS',
    'register_publisher',
    'get_publisher',
    'list_topics',
    'HandPosePublisher',
]
