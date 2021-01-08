FROM analyticdelta/python3.8-slim-buster-with-texlive:v1.0

COPY depends /installs
COPY requirements.txt /installs

# FIXME Move pandoc into the creation of the base image so as to
# always get the latest.
# Install latest pandoc
RUN dpkg -i /installs/pandoc-2.10.1-1-amd64.deb

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

# FIXME docker-compose.yaml provides an entrypoint for the api that
# launches uvicorn so we don't need it here.
# COPY entrypoint.sh  /root/entrypoint.sh
# RUN chmod +x /root/entrypoint.sh

# Launch entrypoint.sh
# ENTRYPOINT /root/entrypoint.sh

# FIXME Make host and port env variables and use those same variables
# in config.py also.
# Start FastAPI
# CMD ["uvicorn", "--host", "0.0.0.0", "--port", "5005", "--reload", "src.document.entrypoints.app:app"]
