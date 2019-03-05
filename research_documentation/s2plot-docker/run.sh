#!/bin/sh

# socat TCP-LISTEN:6000,reuseaddr,fork UNIX-CLIENT:\"$DISPLAY\" &

# xhost + # allow connections to X server
IP=10.13.0.85
xhost + $IP
# docker run -e DISPLAY=host.docker.internal:0 -i -t s2plot $COMMAND
docker run -ti -e DISPLAY=$IP:0 -v /tmp/.X11-unix:/tmp/.X11-unix s2plot:latest bash

#-v="/tmp/.X11-unix:/tmp/.X11-unix:rw"
