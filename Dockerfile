FROM python:3.9.5-slim-buster


RUN apt-get update && apt-get install -y \
    wget \
    curl \
    # fonts-noto \ # Was used by old LaTeX system
    fontconfig \
    git \
    lmodern \ # Not sure this is needed anymore
    unzip \
    # Next packages are for wkhtmltopdf
    libxrender1 \
    xfonts-75dpi \
    xfonts-base \
    libjpeg62-turbo

# Install wkhtmltopdf
# Source: https://github.com/wkhtmltopdf/wkhtmltopdf/issues/2037
# Source: https://gist.github.com/lobermann/ca0e7bb2558b3b08923c6ae2c37a26ce
# How to get wkhtmltopdf - don't use what Debian provides as it can have
# headless display issues that mess with wkhtmltopdf.
ARG WKHTMLTOX_LOC # Make a build arg available to this Dockerfile
RUN WKHTMLTOX_TEMP="$(mktemp)" && \
    wget -O "$WKHTMLTOX_TEMP" ${WKHTMLTOX_LOC} && \
    dpkg -i "$WKHTMLTOX_TEMP" && \
    rm -f "$WKHTMLTOX_TEMP"

# Temporary workaround for broken translations.json upstream
COPY working/temp/translations.json /working/temp/

COPY icon-tn.png .
COPY requirements.txt .
COPY requirements-dev.txt .
COPY setup.cfg .
COPY pyproject.toml .

RUN pip install -r requirements.txt
RUN pip install -r requirements-dev.txt

COPY ./src/ /src/
COPY ./tests /tests

# Note: for development, first install your app,
# pip install -e .
# before running your Docker commands, e.g., make unit-tests.

# Note: For production the requirements.in will be modified to include
# this project's remote git repo using the git+https pip-install
# format. See the entry in requirements.in for USFM-Tools as an example.

# Note: For development or production, you'll also need to provide the
# required environment variables as found in the .env file.
