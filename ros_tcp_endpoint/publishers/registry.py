"""
Simple registry for ROS topic publishers using a global dictionary.
"""

from typing import Type
from functools import wraps

# Global registry: topic -> publisher_class
PUBLISHERS = {}


def register_publisher(message_class: Type):
    """
    Decorator to register a publisher class for a message type.
    
    Usage:
        @register_publisher(ManoLandmarks)
        class HandPosePublisher(RosPublisher):
            ...
    
    Args:
        topic: The ROS topic name
        message_class: The ROS message class type
    """
    def decorator(publisher_class):
        PUBLISHERS[message_class] = {
            'class': publisher_class,
            'message_class': message_class
        }
        return publisher_class
    return decorator


def get_publisher(message_class: Type):
    """
    Get publisher info for a message class.
    
    Args:
        message_class: The message class to look up.
        
    Returns:
        Dictionary with 'class' and 'message_class', or None if not found
    """
    return PUBLISHERS.get(message_class, None)


def list_topics():
    """Get list of all registered message classes."""
    return list(PUBLISHERS.keys())
