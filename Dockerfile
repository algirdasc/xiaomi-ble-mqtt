FROM fedora:latest

VOLUME /config
WORKDIR /usr/src/app

RUN dnf install glib2-devel make gcc -y && \
    pip3 install --no-cache-dir mitemp_bt bluepy paho-mqtt && \
    dnf clean all

RUN groupadd -g 9999 appuser && \
    useradd -r -u 9999 -g appuser appuser && \
    chown appuser.appuser /usr/src/app/
USER appuser

COPY . /usr/src/app/

CMD [ "/usr/src/app/run.sh" ]
