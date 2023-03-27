FROM python:3.11-slim-bullseye

RUN apt-get update && apt-get install -y \
    wget \
    curl \
    git \
    unzip \
    # For mypyc
    gcc \
    # For ebook-convert
    xz-utils \
    xdg-utils \
    libegl1 \
    libopengl0 \
    libegl1 \
    libopengl0 \
    libxcb-xinerama0 \
    libxkbcommon0 \
    libglx0 \
    libnss3

# Get and install needed fonts.
RUN cd /tmp \
    && git clone --depth 1 https://github.com/Bible-Translation-Tools/ScriptureAppBuilder-pipeline \
    && cp /tmp/ScriptureAppBuilder-pipeline/ContainerImage/home/fonts/*.ttf /usr/share/fonts/
# Refresh system font cache.
RUN fc-cache -f -v

# Get and install calibre for use of its ebook-convert binary for HTML
# to ePub conversion.
RUN wget -nv -O- https://download.calibre-ebook.com/linux-installer.sh | sh /dev/stdin install_dir=/calibre-bin isolated=y

WORKDIR /app

# Make the output directory where resource asset files are cloned or
# downloaded and unzipped.
RUN mkdir -p working/temp
# Make the output directory where generated HTML and PDFs are placed.
RUN mkdir -p working/output
# Make the output directory where generated documents (PDF, ePub, Docx) are copied too.
RUN mkdir -p document_output

COPY .env .
COPY pyproject.toml .
COPY ./backend/requirements.txt .
COPY ./backend/requirements-prod.txt .
COPY template.docx .

# See https://pythonspeed.com/articles/activate-virtualenv-dockerfile/
# for why a Python virtual env is used inside Docker.
ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv ${VIRTUAL_ENV}
ENV PATH=${VIRTUAL_ENV}/bin:${PATH}

RUN pip install -v --upgrade pip
RUN pip install -v cython
RUN pip install -v -r requirements.txt
RUN pip install -v -r requirements-prod.txt
RUN cd /tmp && git clone -b develop --depth 1 https://github.com/linearcombination/USFM-Tools
RUN cd /tmp/USFM-Tools && python setup.py build install
RUN cp -r /tmp/USFM-Tools/usfm_tools ${VIRTUAL_ENV}/lib/python3.11/site-packages/
RUN pip install weasyprint

COPY ./backend ./backend
COPY ./tests ./tests

# Inside the Python virtual env: check types, install any missing mypy stub
# types packages, and transpile most modules into C using mypyc which
# in turn build them with the resident C compiler, usually clang or
# gcc.
RUN cd backend && mypyc --strict --install-types --non-interactive --verbose document/domain/assembly_strategies/assembly_strategies.py document/domain/parsing.py document/domain/resource_lookup.py # document/domain/document_generator.py

# Make sure Python can find the code to run
ENV PYTHONPATH=/app/backend:/app/tests
