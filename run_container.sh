#!/bin/bash

# TAG=${1:-latest}
# IMAGE_ID=$(docker image ls | awk -v TAG=${TAG} '{ if ($1 == "gitlab-registry.cern.ch/alice-its3-wp3/its-corryvreckan-tools" && $2 == TAG) print $3 }')
# DIGEST=$(docker images --digests | awk -v TAG=${TAG} '{ if ($1 == "gitlab-registry.cern.ch/alice-its3-wp3/its-corryvreckan-tools" && $2 == TAG) print $3 }' | cut -d':' -f2)
# DIGEST=${DIGEST:0:7}

# echo "its-corryvreckan-tools: $(git describe --dirty=M --always)"
# echo "Running tag '${TAG}', image ID '${IMAGE_ID}', digest '${DIGEST}'"

# docker run --rm -it \
#        -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix -e XAUTHORITY=$XAUTHORITY -v $XAUTHORITY:$XAUTHORITY \
#        --mount type=bind,source="$(pwd)"/,target=/local \
#        -e IMAGE_ID=${IMAGE_ID} \
#        gitlab-registry.cern.ch/alice-its3-wp3/its-corryvreckan-tools:${TAG} \
#        /bin/bash

TAG=${1:-temp}
IMAGE_ID=$(docker image ls | awk -v TAG=${TAG} '{ if ($1 == "corrytools" && $2 == TAG) print $3 }')
DIGEST=$(docker images --digests | awk -v TAG=${TAG} '{ if ($1 == "corrytools" && $2 == TAG) print $3 }' | cut -d':' -f2)
DIGEST=${DIGEST:0:7}

docker run --rm -it \
         -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix -e XAUTHORITY=$XAUTHORITY -v $XAUTHORITY:$XAUTHORITY \
         --mount type=bind,source="$(pwd)"/,target=/local \
         -e IMAGE_ID=${IMAGE_ID} \
          corrytool:${TAG} \
          /bin/bash
