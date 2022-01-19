FROM python:3.10.2-slim-bullseye

RUN apt-get update && apt-get install -y \
    wget \
    curl \
    git \
    unzip \
    # Next packages are for wkhtmltopdf
    fontconfig \
    fonts-noto-cjk \
    libxrender1 \
    xfonts-75dpi \
    xfonts-base \
    libjpeg62-turbo \
    # For mypyc
    gcc

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
# Make the output directory where generated PDFs are copied too.
RUN mkdir -p /pdf_output

COPY .env .
COPY icon-tn.png .
COPY ./backend/gunicorn.conf.py .

# See https://pythonspeed.com/articles/activate-virtualenv-dockerfile/
# for why a Python virtual env is used inside Docker.
ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY ./backend/requirements.txt .
COPY ./backend/requirements-prod.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements-prod.txt

COPY ./backend/ /backend/
COPY ./tests/ /tests/
# COPY ./language_codes.json /tests/

# Inside the Python virtual env: check types, install any missing mypy stub
# types packages, and compile most modules into C using mypyc
RUN cd $VIRTUAL_ENV && . $VIRTUAL_ENV/bin/activate && mypyc --strict --install-types --non-interactive /backend/document/**/*.py

# Make sure Python can find the code to run
ENV PYTHONPATH=/backend:/tests

# Run tests to verify correctness and (mainly) to generate assets for preheating cache
# To run the tests do: docker-compose build --build-arg run_tests=1
# Make RUN_TESTS in .env and referenced in docker-compose.yml
# available here.
ARG RUN_TESTS=false
RUN if [ "$RUN_TESTS" = "true" ] ; then IN_CONTAINER=true pytest /tests/ ; else echo You have chosen to skip the test suite ; fi

# What gets run when 'docker-compose run backend' is executed.
CMD ["gunicorn", "--name", "document:entrypoints:app", "--worker-class", "uvicorn.workers.UvicornWorker", "--pythonpath", "/backend", "--conf", "/backend/gunicorn.conf.py", "document.entrypoints.app:app"]
