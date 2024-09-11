# 使用一个轻量级的基础镜像，如 Debian 或 Ubuntu
FROM arm64v8/ubuntu:20.04

# 设置环境变量以避免在安装时交互
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Geneva

# 更新并安装必要的软件包
RUN apt-get update && \
    apt-get install -y \
        curl cmake software-properties-common g++ gcc binutils git nano vim tmux \
        wget build-essential libssl-dev zlib1g-dev libbz2-dev clang-format-12 libeigen3-dev \
        libreadline-dev libsqlite3-dev libncursesw5-dev xz-utils tk-dev libxml2-dev \
        libxmlsec1-dev libffi-dev liblzma-dev libxpm-dev python3-pip python3-distutils \
        && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# 添加 Python 3.10 的 PPA 并安装 Python 3.10，移除 Python 3.8
RUN add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && apt-get install -y python3.10 python3.10-dev python3.10-venv && \
    apt-get autoremove -y && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 2 && \
    wget https://bootstrap.pypa.io/get-pip.py && python3.10 get-pip.py && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# 安装 sw
ENV SWPATH="/opt/sw"
COPY contrib/sw ${SWPATH}
RUN cd ${SWPATH} && \
    python3 -m pip install --upgrade pip && \
    python3 -m pip install -r requirements.txt && \
    make install && \
    pip3 install .

# 安装 EUDAQ2
ENV EUDAQ2PATH="/opt/eudaq2"
COPY contrib/eudaq2 ${EUDAQ2PATH}
RUN cd ${EUDAQ2PATH} && \
    git checkout f0087d18f040a3c70d4c81cfab9526118d070e3d && \
    mkdir -p build && cd build && \
    cmake -DEUDAQ_BUILD_STDEVENT_MONITOR=ON \
          -DUSER_ITS3_BUILD=ON \
          -DEUDAQ_BUILD_PYTHON=ON \
           .. && \
    make -j$(nproc) && make install

# Add layer for ROOT6
ENV ROOT6_VERSION=6.26.16
ENV ROOTSYS="/opt/root6"
ENV PATH="$ROOTSYS/bin:$PATH"

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

# 安装 Corryvreckan
ENV CORRYPATH="/opt/corryvreckan"
COPY contrib/corryvreckan ${CORRYPATH}
RUN cd ${CORRYPATH} && \
    mkdir -p build && cd build && \
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
    make -j$(nproc) && make install


# 设置环境变量
ENV PATH="${CORRYPATH}/bin:${ROOTSYS}/bin:${SWPATH}/bin:${PATH}"
ENV LD_LIBRARY_PATH="${EUDAQ2PATH}/lib:${ROOTSYS}/lib:${LD_LIBRARY_PATH}"
ENV PYTHONPATH="${EUDAQ2PATH}/lib:${ROOTSYS}/lib:${PYTHONPATH}"

# 设置工作目录
WORKDIR /local/

# 默认启动命令
CMD ["bash"]