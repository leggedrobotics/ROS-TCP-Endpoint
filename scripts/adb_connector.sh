#!/bin/bash

PORT=${1:-10000}
echo "Starting persistent ADB reverse monitor for port $PORT..."

cleanup() {
    echo "ROS shutdown detected. Removing ADB reverse for port $PORT..."
    adb reverse --remove "tcp:$PORT"
    exit 0
}

trap cleanup SIGTERM SIGINT

sleep 5

while true; do
    # 1. Wait for any device to be connected via USB
    adb wait-for-device > /dev/null 2>&1
    
    # 2. Apply the reverse port forwarding
    echo "Device detected. Applying reverse tcp:$PORT..."
    adb reverse "tcp:$PORT" "tcp:$PORT" > /dev/null 2>&1   

    # 3. Wait until the device is disconnected
    while [ "$(adb get-state 2>/dev/null)" == "device" ]; do
        sleep 2
        wait $!
    done

    echo "Device disconnected. Waiting for reconnection..."
done