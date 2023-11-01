# BSD 2-Clause License

# Copyright (c) 2020, Supreeth Herle
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

FROM ubuntu:focal as builder

ENV DEBIAN_FRONTEND=noninteractive

# Install updates and dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3-pip \
        python3-setuptools \
        python3-wheel \
        ninja-build \
        build-essential \
        flex \
        bison \
        git \
        cmake \
        libsctp-dev \
        libgnutls28-dev \
        libgcrypt-dev \
        libssl-dev \
        libidn11-dev \
        libmongoc-dev \
        libbson-dev \
        libyaml-dev \
        meson \
        mongodb \
        curl \
        gnupg \
        ca-certificates \
        libmicrohttpd-dev \
        libcurl4-gnutls-dev \
        libnghttp2-dev \
        libtins-dev \
        libidn11-dev \
        libtalloc-dev


##

# Update the package list and install required packages
RUN apt-get update && apt-get install -y ca-certificates curl gnupg

# Create the /etc/apt/keyrings directory
RUN mkdir -p /etc/apt/keyrings

# Add the Node.js GPG key to /etc/apt/keyrings/nodesource.gpg
RUN curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg

# Set the Node.js major version you want (replace with the desired version)
ENV NODE_MAJOR=20

# Add the Node.js repository to sources.list.d
RUN echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_$NODE_MAJOR.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list

# Update the package list and install Node.js
RUN apt-get update && apt-get install nodejs -y
#

# Get open5gs code and install
RUN git clone --recursive https://github.com/open5gs/open5gs && cd open5gs && \
    git checkout tags/v2.6.6 && meson build --prefix=`pwd`/install && \
    ninja -C build && cd build && ninja install && \
    mkdir -p /open5gs/install/include

# Building WebUI of open5gs
RUN cd open5gs/webui && npm ci

# Build final image
FROM ubuntu:focal

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        ca-certificates \
        libssl-dev \
        libyaml-dev \
        libmicrohttpd-dev \
        libmongoc-dev \
        libsctp-dev \
        libcurl4-gnutls-dev \
        libtins-dev \
        libidn11-dev \
        libtalloc-dev \
        netbase \
        ifupdown \
        net-tools \
        iputils-ping \
        python3-setuptools \
        python3-wheel \
        python3-pip \
        iptables \
        iperf \
        gnupg && \
    apt-get autoremove -y && apt-get autoclean

RUN pip3 install click


# RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && apt-get install -y nodejs && \
#     apt-get remove -y curl && apt-get autoremove -y && apt-get autoclean
# Update the package list and install required packages
RUN apt-get update && apt-get install -y ca-certificates curl gnupg

# Create the /etc/apt/keyrings directory
RUN mkdir -p /etc/apt/keyrings

# Add the Node.js GPG key to /etc/apt/keyrings/nodesource.gpg
RUN curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg

# Set the Node.js major version you want (replace with the desired version)
ENV NODE_MAJOR=20

# Add the Node.js repository to sources.list.d
RUN echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_$NODE_MAJOR.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list

# Update the package list and install Node.js
RUN apt-get update && apt-get install nodejs -y


RUN update-ca-certificates

COPY --from=builder /open5gs/install/bin /open5gs/install/bin
COPY --from=builder /open5gs/install/etc /open5gs/install/etc
COPY --from=builder /open5gs/install/include /open5gs/install/include
COPY --from=builder /open5gs/install/lib /open5gs/install/lib
COPY --from=builder /open5gs/webui /open5gs/webui

# Set the working directory to open5gs
WORKDIR open5gs

COPY open5gs_init.sh /
CMD /open5gs_init.sh