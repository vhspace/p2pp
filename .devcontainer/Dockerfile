FROM mcr.microsoft.com/devcontainers/python:3.8

ENV DEBIAN_FRONTEND=noninteractive
ENV QT_DEBUG_PLUGINS=1
ENV PYTHONPATH=/workspace
ENV QT_QPA_PLATFORM=xcb

# Update package list and install basic dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libegl1 \
    libgl1 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-shape0 \
    libxcb-sync1 \
    libxcb-xfixes0 \
    libxcb-xinerama0 \
    libxcb-xkb1 \
    libxkbcommon-x11-0 \
    libxtst6 \
    libxcb-dri3-0 \
    libxcb-glx0 \
    libxcursor1 \
    libxi6 \
    libxrender-dev \
    python3-pip \
    python3-pyqt5 \
    python3-pyqt5.qtwebengine \
    qttools5-dev-tools \
    qttools5-dev \
    libssl-dev \
    python3-openssl \
    libxcb1 \
    libx11-xcb-dev \
    libglu1-mesa-dev \
    libxi-dev \
    libxkbcommon-dev \
    libxkbcommon-x11-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace


