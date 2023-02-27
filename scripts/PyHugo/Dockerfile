# syntax=docker/dockerfile:1
FROM ubuntu:22.04

ENV BUILD_DEPS="python3-pip wget gcc" \
    RUN_DEPS="python3" \
    GOLANG_URL_ARM="https://go.dev/dl/go1.20.1.linux-arm64.tar.gz" \
    GOLANG_URL_X86_64="https://go.dev/dl/go1.20.1.linux-amd64.tar.gz"

RUN --mount=target=/mnt/build-context \
    apt-get upgrade && \
    apt-get update && \
    apt-get install -y $BUILD_DEPS $RUN_DEPS && \
    mkdir -p /build && \
    case `uname -m` in aarch64) DOWNLOAD_URL=$GOLANG_URL_ARM;; \
      arm64) DOWNLOAD_URL=$GOLANG_URL_ARM;; \
      x86_64) DOWNLOAD_URL=$GOLANG_URL_X86_64;; esac && \
    #DOWNLOAD_URL=$GOLANG_URL_ARM
    ARCHIVE=`basename "$DOWNLOAD_URL"` && \
    echo "Downloading $DOWNLOAD_URL (`uname -m`) to $ARCHIVE" && \
    wget --progress=bar $DOWNLOAD_URL && \
    tar -C /usr/local -xzf $ARCHIVE && \
    rm $ARCHIVE && \
    cp -r /mnt/build-context/* /build/ && \
    cd /build && \
    pip install -r requirements.txt && \
    PATH=$PATH:/usr/local/go/bin python3 setup.py install && \
    cd .. && \
    rm -rf /build /usr/local/go ~/go ~/.cache && \
    apt remove -y $BUILD_DEPS && \
    apt autoremove -y
