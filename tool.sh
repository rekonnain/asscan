#!/bin/bash

cmd=$1

PLATFORM=amd64
TAG=asscan

if [ "$1" == "build" ] ; then
    docker build --platform $PLATFORM -t $TAG -f Dockerfile .
elif [ "$1" == "run" ] ; then
    docker run --rm -it -v `pwd`/stuff:/stuff  -t $TAG
elif [ "$1" == "shell" ] ; then
    docker run --rm --net=host -v /home/john/tmp:/stuff -it $TAG bash
fi


