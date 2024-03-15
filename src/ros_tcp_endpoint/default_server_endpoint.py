#!/usr/bin/env python3

import rospy

from ros_tcp_endpoint import TcpServer


def main(args=None):
    # Start the Server Endpoint
    rospy.init_node("unity_endpoint", anonymous=True)
    tcp_server = TcpServer(rospy.get_name(), buffer_size=1024*4)
    tcp_server.start()
    rospy.spin()


if __name__ == "__main__":
    main()
