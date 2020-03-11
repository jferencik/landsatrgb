FROM debian:stable
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y  python3-rasterio python3-matplotlib python3-cartopy python3-scipy \
    && apt-get clean
