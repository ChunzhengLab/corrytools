FROM arm64v8/ubuntu:20.04
LABEL maintainer = "Chunzheng Wang <chunzheng.wang@icloud.com>"

# Install basic build requirements
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Geneva
RUN apt-get update
RUN apt-get install -y curl cmake g++ gcc binutils git nano vim tmux

# Install ROOT dependencies
RUN apt-get install -y dpkg-dev libx11-dev libxpm-dev libxft-dev libxext-dev libssl-dev python3 python3-dev python3-pip python3-tk python-is-python3

# Install Corryvreckan dependencies
RUN apt-get install -y libeigen3-dev python3-lxml clang-format-12

# Install helpful Python packages
RUN pip3 install --upgrade pip && \
    pip3 install numpy matplotlib scipy pandas


# Add layer for ROOT6
ENV ROOT6_VERSION=6.26.14
ENV ROOTSYS="/opt/root6"
ENV PATH="$ROOTSYS/bin:$PATH"
ENV LD_LIBRARY_PATH="$ROOTSYS/lib:$LD_LIBRARY_PATH"
ENV LIBPATH="$ROOTSYS/lib:$LIBPATH"
ENV PYTHONPATH="$ROOTSYS/lib:$PYTHONPATH"
ENV CMAKE_PREFIX_PATH="$ROOTSYS:$CMAKE_PREFIX_PATH"

RUN mkdir -p ${ROOTSYS}/src && mkdir -p ${ROOTSYS}/build && \
    curl -o ${ROOTSYS}/root.${ROOT6_VERSION}.tar.gz \
            https://root.cern.ch/download/root_v${ROOT6_VERSION}.source.tar.gz && \
    tar zxf ${ROOTSYS}/root.${ROOT6_VERSION}.tar.gz -C ${ROOTSYS}/src && \
    rm -f ${ROOTSYS}/root.${ROOT6_VERSION}.tar.gz && \
    cd ${ROOTSYS}/build && \
    cmake -Dgdml=ON \
           -Dgenvector=ON \
           -Dmathmore=ON \
           -Dminuit2=ON \
           -Dthread=ON \
           -Dx11=ON \
           -Dopengl=ON \
           -Dasimage=ON \
           -Dcocoa=ON \
           -Dtmva=OFF -Dtmva-cpu=OFF -Dtmva-pymva=OFF \
           -Dhttp=OFF \
           -Dwebgui=OFF \
           -Droot7=OFF \
           -Dfftw3=OFF \
           -Dfitsio=OFF \
           -Dclad=OFF \
           -Dspectrum=OFF \
           -Dvdt=OFF \
           -Dxrootd=OFF \
           -Droofit=OFF \
           -Ddataframe=OFF \
           -Dpython3=ON \
           -DPYTHON_EXECUTABLE=/usr/bin/python3 \
           -DCMAKE_INSTALL_PREFIX=../ \
           -DCMAKE_CXX_STANDARD=17 \
           ../src/root-${ROOT6_VERSION} && \
    make -j`grep -c processor /proc/cpuinfo` && \
    make install && \
    rm -rf ${ROOTSYS}/src && rm -rf ${ROOTSYS}/build

# MLR1 DAQ software (e.g. used in APTSDump.py)
ENV MLR1SWPATH=/opt/apts-dpts-ce65-daq-software
COPY contrib/apts-dpts-ce65-daq-software ${MLR1SWPATH}
ENV mlr1sw_REV_INST=316c10564764e98ea961d6cbf4bbe0d214fc351d
RUN cd ${MLR1SWPATH} && \
    git checkout ${mlr1sw_REV_INST} && \
    pip3 install .

# EUDAQ2
ENV EUDAQ2PATH="/opt/eudaq2"
COPY contrib/eudaq2 ${EUDAQ2PATH}
ENV eudaq2_REV_INST=f0087d18f040a3c70d4c81cfab9526118d070e3d
RUN cd ${EUDAQ2PATH} && \
    git checkout ${eudaq2_REV_INST}
RUN mkdir -p ${EUDAQ2PATH}/build && \
    cd ${EUDAQ2PATH}/build && \
    cmake -DEUDAQ_BUILD_STDEVENT_MONITOR=ON \
          -DUSER_ITS3_BUILD=ON \
          -DEUDAQ_BUILD_PYTHON=ON \
          .. && \
    make -j`grep -c processor /proc/cpuinfo` && \
    make install

# Corryvreckan
ENV CORRYPATH=/opt/corryvreckan
COPY contrib/corryvreckan ${CORRYPATH}
# ENV corry_REV_INST=d918c29bd9093db13ac5d6a69bf7edccc1dd9704
# RUN cd ${CORRYPATH} && \
#     git checkout ${corry_REV_INST}
RUN mkdir -p ${CORRYPATH}/build && \
    cd ${CORRYPATH}/build && \
    cmake -DBUILD_EventLoaderEUDAQ=OFF \
          -DBUILD_EventLoaderATLASpix=OFF \
          -DBUILD_EventLoaderCLICpix=OFF \
          -DBUILD_EventLoaderCLICpix2=OFF \
          -DBUILD_EventLoaderMuPixTelescope=OFF \
          -DBUILD_EventLoaderTimepix1=OFF \
          -DBUILD_EventLoaderTimepix3=OFF \
          -DCMAKE_INSTALL_PREFIX=../ \
          -DBUILD_EventLoaderEUDAQ2=ON \
          -Deudaq_DIR=${EUDAQ2PATH}/cmake \
          .. && \
    make -j`grep -c processor /proc/cpuinfo` && \
    make install

# Print software versions when running the container
RUN echo "source /local/.print_image_id.sh" >> "/root/.bashrc"

# Default command for starting the container, executed after the ENTRYPOINT
ENV PATH "${CORRYPATH}/bin:${PATH}"
ENV LD_LIBRARY_PATH "${EUDAQ2PATH}/lib:${LD_LIBRARY_PATH}"
ENV PYTHONPATH "${EUDAQ2PATH}/lib:${PYTHONPATH}"
WORKDIR /local/
CMD ["bash"]
