FROM ubuntu:24.04

RUN apt-get update && apt-get install -y python3-pip libcairo2-dev libgirepository1.0-dev gobject-introspection python3-gi gir1.2-gtk-3.0 && pip3 install --break-system-packages uv

CMD /bin/bash