FROM debian:latest

# Install packages
RUN apt update && apt install -y \
    context \
    curl \
    dos2unix \
    fonts-noto \
    pandoc \
    python \
    python-pip \
    texlive-fonts-recommended \
    texlive-xetex \
    wget

# Install python packages
RUN pip install --upgrade pip \
 && pip install \
    usfm-tools

# Clean up run image
RUN apt-get purge -y --auto-remove \
                  -o APT::AutoRemove::RecommendsImportant=false \
 && rm -rf /var/lib/apt/lists/* \
           /tmp/*

# Setup working volume
VOLUME "/working"

# Setup entrypoint (convert files to unix so we can run on Windows too)
COPY [".", "."]
RUN find . -name "*.sh" -print | xargs dos2unix \
 && find . -name "*.py" -print | xargs dos2unix \
 && chmod +x ./uwb/bible/pdf_export.sh
ENTRYPOINT ["./uwb/bible/pdf_export.docker_entrypoint.sh"]
