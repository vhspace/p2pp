FROM mcr.microsoft.com/devcontainers/python:3.12

ENV DEBIAN_FRONTEND=noninteractive
ENV QT_DEBUG_PLUGINS=1
ENV PYTHONPATH=/workspace
ENV QT_QPA_PLATFORM=xcb
ENV DISPLAY=:1

# Update package list and install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Qt and GUI dependencies
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
    libxcb1 \
    libx11-xcb-dev \
    libglu1-mesa-dev \
    libxi-dev \
    libxkbcommon-dev \
    libxkbcommon-x11-dev \
    # Python and PyQt5 system packages
    python3-pip \
    python3-pyqt5 \
    python3-pyqt5.qtwebengine \
    python3-pyqt5.qtwebkit \
    qttools5-dev-tools \
    qttools5-dev \
    libssl-dev \
    python3-openssl \
    # Build tools and dependencies
    build-essential \
    pkg-config \
    # Testing dependencies (for headless GUI testing)
    xvfb \
    xauth \
    # Development tools
    git \
    curl \
    wget \
    unzip \
    # Build dependencies for Python packages
    libffi-dev \
    libcairo2-dev \
    libpango1.0-dev \
    libgdk-pixbuf2.0-dev \
    shared-mime-info \
    # File compression tools (for build packages)
    rpm \
    debhelper \
    python3-all \
    dh-python \
    python3-setuptools \
    python3-stdeb \
    && rm -rf /var/lib/apt/lists/*

# Install uv (fast Python package manager)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

# Upgrade pip for compatibility
RUN pip install --upgrade pip

# Create workspace directory
WORKDIR /workspace

# Create cache directory for uv
RUN mkdir -p /workspace/.uv-cache
ENV UV_CACHE_DIR=/workspace/.uv-cache

# Set up virtual display for headless GUI testing
RUN echo '#!/bin/bash\nXvfb :1 -screen 0 1024x768x24 > /dev/null 2>&1 &' > /usr/local/bin/start-xvfb \
    && chmod +x /usr/local/bin/start-xvfb

# Create a non-root user for development (optional but recommended)
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && chown -R $USERNAME:$USERNAME /workspace

# Switch to non-root user
USER $USERNAME

# Set up shell for the user
RUN echo 'export PATH="/home/vscode/.cargo/bin:$PATH"' >> /home/vscode/.bashrc \
    && echo 'export UV_CACHE_DIR=/workspace/.uv-cache' >> /home/vscode/.bashrc \
    && echo 'alias ll="ls -la"' >> /home/vscode/.bashrc \
    && echo 'alias pytest="uv run test"' >> /home/vscode/.bashrc

# Install uv for the user as well
USER $USERNAME
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/home/vscode/.cargo/bin:$PATH"

WORKDIR /workspace


