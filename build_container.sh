# #!/bin/bash

# #build container as :temp, generate timestamp, tag container accordingly
# docker login gitlab-registry.cern.ch
# docker build -t gitlab-registry.cern.ch/alice-its3-wp3/its-corryvreckan-tools:temp .

# timestamp=$(docker inspect -f '{{ .Created }}' gitlab-registry.cern.ch/alice-its3-wp3/its-corryvreckan-tools:temp | tr -d '-' | tr 'T' '_' | tr -d ':' | cut -d'.' -f1 | tr ' ' '_')
# tools_REV=$(git describe --dirty=M --always)
# tag="${timestamp}__${tools_REV}"

# docker tag gitlab-registry.cern.ch/alice-its3-wp3/its-corryvreckan-tools:temp gitlab-registry.cern.ch/alice-its3-wp3/its-corryvreckan-tools:"${tag}"

# #tag container, if first option gives a tag
# if [[ "$1" != "push" ]] && [[ $# -ge 1 ]]
# then
#     docker tag gitlab-registry.cern.ch/alice-its3-wp3/its-corryvreckan-tools:temp gitlab-registry.cern.ch/alice-its3-wp3/its-corryvreckan-tools:"$1"
# fi

# #push container, if first option is push. Push with tag if second option is a tag
# if [[ "$1" == "push" ]]
# then
#     docker push gitlab-registry.cern.ch/alice-its3-wp3/its-corryvreckan-tools:"${tag}"
#     if [[ $# -ge 2 ]]
#     then
#         docker tag gitlab-registry.cern.ch/alice-its3-wp3/its-corryvreckan-tools:temp gitlab-registry.cern.ch/alice-its3-wp3/its-corryvreckan-tools:"$2"
#         docker push gitlab-registry.cern.ch/alice-its3-wp3/its-corryvreckan-tools:"$2"
#     fi
# fi

# docker rmi gitlab-registry.cern.ch/alice-its3-wp3/its-corryvreckan-tools:temp

docker build -t corrytool:temp .
