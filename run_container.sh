#!/bin/bash
docker run --rm -it \
         --mount type=bind,source="$(pwd)"/,target=/local \
          moss_tool:private \
          /bin/bash
