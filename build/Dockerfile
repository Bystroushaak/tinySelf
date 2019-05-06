FROM ubuntu:19.04

VOLUME /build
VOLUME /release

USER root

RUN apt-get update && apt-get install -y \
    git \
    mercurial \
    build-essential \
    pkg-config \
    gcc \
    devscripts \
    fakeroot \
    debhelper \
    curl \
    libffi-dev \
    libffi6 \
    pypy

RUN git clone https://github.com/Bystroushaak/tinySelf.git /src && \
    hg clone https://bitbucket.org/pypy/pypy /pypy && \
    curl https://bootstrap.pypa.io/get-pip.py | pypy - --user && \
    curl https://bootstrap.pypa.io/get-pip.py | python - --user && \
    pypy -m pip install --user -U git+https://github.com/alex/rply.git && \
    python -m pip install -r /src/metadata/requirements.txt

COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

WORKDIR /src

ENTRYPOINT ["/entrypoint.sh"]
