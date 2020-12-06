FROM analyticdelta/python3.8-slim-buster-with-texlive:v1.0

COPY depends /installs

# Install latest pandoc
RUN dpkg -i /installs/pandoc-2.10.1-1-amd64.deb

# Install specific fonts
RUN mkdir -p ~/.local/share/fonts/Raleway \
    && unzip /installs/Raleway.zip -d ~/.local/share/fonts/Raleway \
    && fc-cache -f -v

# Clean up
RUN rm -r /installs && rm -rf /var/lib/apt/lists/*

RUN pip install -r /installs/requirements.txt

RUN mkdir -p /working/temp
COPY ["icon-tn.png", "/working/temp"]

RUN mkdir -p /src
COPY src/ /src/
RUN pip install -e /src
COPY tests/ /tests/

WORKDIR /src

# COPY ["entrypoint.sh", "/root/entrypoint.sh"]
# RUN chmod +x /root/entrypoint.sh

# Launch entrypoint.sh
ENTRYPOINT /root/entrypoint.sh
