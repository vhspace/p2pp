FROM mcr.microsoft.com/devcontainers/python:3.8

ENV DEBIAN_FRONTEND=noninteractive
ENV QT_DEBUG_PLUGINS=1
ENV PYTHONPATH=/workspace
ENV QT_QPA_PLATFORM=xcb

# The base devcontainer image can include a Yarn APT source without its GPG key
# in some environments. Remove it to keep apt-get update reliable.
RUN rm -f /etc/apt/sources.list.d/yarn.list /etc/apt/sources.list.d/yarn.sources || true

# Update package list and install basic dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    gpg \
    git \
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
    && curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | gpg --dearmor -o /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" > /etc/apt/sources.list.d/github-cli.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends gh \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

WORKDIR /workspace


