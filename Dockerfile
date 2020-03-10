#FROM ubuntu:18.04
from debian:stable
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y  python3-rasterio python3-matplotlib python3-cartopy python3-scipy \
    && apt-get clean
RUN mkdir /home/landsat/
COPY solution.py /home/landsat/landsatrgb.py
# CMD python3 /home/axel/landsatrgb.py