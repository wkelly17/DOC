FROM python:3.9.5-slim-buster

COPY depends /installs
COPY requirements.txt /installs

RUN apt-get update && apt-get install -y \
    wget \
    curl \
    fonts-noto \
    fontconfig \
    git \
    lmodern \
    unzip


# Get and install Pandoc.
# ARG PANDOC_LOC # Make a build arg available to this Dockerfile
# RUN PANDOC_TEMP="$(mktemp)" && \
#     wget -O "$PANDOC_TEMP" ${PANDOC_LOC} && \
#     dpkg -i "$PANDOC_TEMP" && \
#     rm -f "$PANDOC_TEMP"


# FIXME You could possibly use
# gdebi properly handle dependencies.
# RUN apt-get install gdebi-core

# Source: https://github.com/wkhtmltopdf/wkhtmltopdf/issues/2037
# Source: https://gist.github.com/lobermann/ca0e7bb2558b3b08923c6ae2c37a26ce
# How to get wkhtmltopdf - don't use what Debian provides as it can have
# headless display issues that mess with wkhtmltopdf.
# Install wkhtmltopdf
ARG WKHTMLTOX_LOC # Make a build arg available to this Dockerfile
RUN WKHTMLTOX_TEMP="$(mktemp)" && \
    wget -O "$WKHTMLTOX_TEMP" ${WKHTMLTOX_LOC} && \
    apt-get update && \
    apt-get -V install -y fontconfig libxrender1 xfonts-75dpi xfonts-base libjpeg62-turbo && \
    dpkg -i "$WKHTMLTOX_TEMP" && \
    rm -f "$WKHTMLTOX_TEMP"

# Install specific fonts
RUN mkdir -p ~/.local/share/fonts/Raleway \
    && unzip /installs/Raleway.zip -d ~/.local/share/fonts/Raleway \
    && fc-cache -f -v

RUN pip install -r /installs/requirements.txt

# Clean up
RUN rm -r /installs && rm -rf /var/lib/apt/lists/*

# RUN mkdir -p /working/temp
WORKDIR /working/temp
COPY icon-tn.png  /working/temp

WORKDIR /src
COPY src/ /src/
RUN pip install -e /src
COPY tests/ /tests/

WORKDIR /
