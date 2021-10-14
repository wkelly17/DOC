FROM python:3.9.7-slim-buster

RUN apt-get update && apt-get install -y \
    wget \
    curl \
    fontconfig \
    fonts-noto-cjk \
    git \
    unzip \
    # Next packages are for wkhtmltopdf
    libxrender1 \
    xfonts-75dpi \
    xfonts-base \
    libjpeg62-turbo

# Get and install needed fonts.
RUN cd /tmp \
    && git clone --depth 1 https://github.com/Bible-Translation-Tools/ScriptureAppBuilder-pipeline \
    && cp /tmp/ScriptureAppBuilder-pipeline/ContainerImage/home/fonts/*.ttf /usr/share/fonts/
# Refresh system font cache.
RUN fc-cache -f -v

# Install wkhtmltopdf
# Source: https://github.com/wkhtmltopdf/wkhtmltopdf/issues/2037
# Source: https://gist.github.com/lobermann/ca0e7bb2558b3b08923c6ae2c37a26ce
# How to get wkhtmltopdf - don't use what Debian provides as it can have
# headless display issues that mess with wkhtmltopdf.

# Make a build arg available to this Dockerfile with default
ARG WKHTMLTOX_LOC=https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.buster_amd64.deb
RUN WKHTMLTOX_TEMP="$(mktemp)" && \
    wget -O "$WKHTMLTOX_TEMP" ${WKHTMLTOX_LOC} && \
    dpkg -i "$WKHTMLTOX_TEMP" && \
    rm -f "$WKHTMLTOX_TEMP"

# Make the output directory where resource asset files are cloned or
# downloaded and unzipped.
RUN mkdir -p /working/temp
# Make the output directory where generated HTML and PDFs are placed.
RUN mkdir -p /working/output
# Make the directory where logs are written to.

COPY icon-tn.png .
COPY gunicorn.conf.py .

# See https://pythonspeed.com/articles/activate-virtualenv-dockerfile/
ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY requirements.txt .
COPY requirements-dev.txt .
RUN pip install -r requirements.txt
RUN pip install -r requirements-dev.txt

COPY ./src/ /src/
COPY ./tests /tests

ENV PYTHONPATH=/src:/tests

CMD ["gunicorn", "--worker-class", "uvicorn.workers.UvicornWorker", "--config", "./gunicorn.conf.py", "document.entrypoints.app:app"]