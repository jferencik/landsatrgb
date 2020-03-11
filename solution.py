#!/usr/bin/env python3
import matplotlib
matplotlib.use('Agg')
import rasterio
from rasterio.warp import transform_bounds
import os
import logging
import numpy as np
from urllib.request import urlopen
from matplotlib.patches import Polygon
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from cartopy import feature as cfeature

logger = logging.getLogger(__name__)

WORKING_FOLDER = None
BASE_URL = 'http://landsat-pds.s3.amazonaws.com/c1/L8/107/035/LC08_L1TP_107035_20190105_20190130_01_T1/'
BAND_NAME_TEMPLATE = 'LC08_L1TP_107035_20190105_20190130_01_T1_B{band_no:d}.TIF'

landsat_truecolor_bands = {
    'red':4,
    'green':3,
    'blue': 2
}
HTTP_READ_CHUNKSZIE = 1024*10



def urls_from_bands(truecolor_bands=None):
    """
    Create HTTP urls for the red, blue and green Landsat 8  bands from Amazon cloud source
    :param truecolor_bands:  dict, mapping band name to band number
    :return: dict, band name, band url
    """
    urls = dict()
    logger.info(f'Creating urls for bands')
    for name, band_no in truecolor_bands.items():
        remote_band_name = BAND_NAME_TEMPLATE.format(band_no=band_no)
        urls[name] = os.path.join(BASE_URL, remote_band_name)
    return urls

def load_or_download(urls=None, folder_to=None, chunked=True):
    """
    Find requested image paths on local disk.
    If they do not exist download them before.

    :param urls: dict containing image names and remote image urls
    :param folder_to: str, full path to the folder where the images will be stored if they are going to be downloaded
    :param chunked: bool, if true use a chunked approach when downloading data
    :return: dict containing image names (red, green blue) and image path on local disk
    """
    assert os.path.exists(folder_to), f'folder_to={folder_to} does not exist'
    assert os.access(folder_to, os.W_OK), f'folder_to={folder_to} is not writable'
    logger.info(f'Fetching bands...')

    image_paths = dict()

    for name, band_url in urls.items():
        root_url, image_name = os.path.split(band_url)
        local_image_path = os.path.join(folder_to, image_name)
        if not os.path.exists(local_image_path):
            with open(local_image_path, 'wb') as local_image:
                logger.info(f'downloading {name} band from {band_url}')
                with urlopen(band_url) as response:
                    if not chunked:
                        local_image.write(response.read())
                    else:
                        while True:
                            content = response.read(HTTP_READ_CHUNKSZIE)
                            if not content:
                                break
                            local_image.write(content)
                logger.info(f'{name} band was saved to {local_image_path}')
        else:
            logger.info(f'setting {name} band to {local_image_path}')
        image_paths[name] = local_image_path

    return  image_paths



def custom_stretch(band=None, min_percentile=None, max_percentile=None, power_scale=None, nodata_value=None):
    """
     Custom strech an Landsat8 band so the visualisation experience is enhanced when creating
    an RGB true colour product. Performs folowing steps in the specified order
        mask band using nodata_value.
        compute min and max values using min and max percentiles
        cuts off the min and max values
        rescales the input band from original values to 0-255 range optionally applying power scaling
        converts the 2 byte band to 1 byte


    :param band: numpy array representing the band
    :param min_percentile: float, the percenatile vaue used to compute the minimum value
    :param max_percentile: float, the percentile value used to compute the maximum value
    :param power_scale: float, the band will be scaled with inverse of this value
    :param nodata_value: int, the value that corresponds to background in the band
    :return: scaled(unisgned 8 bit) and stretched band
    """



    band_mask = band != nodata_value
    valid_band = band[band_mask]
    band_min = np.percentile(valid_band,q=min_percentile)
    band_max = np.percentile(valid_band,q=max_percentile)
    valid_band[valid_band < band_min] = band_min
    valid_band[valid_band>band_max] = band_max
    if power_scale is not None:
        temp_arr = ((valid_band-band_min)/(band_max-band_min))**(1./power_scale)*255
    else:
        temp_arr = ((valid_band-band_min)/(band_max-band_min))*255
    streched = np.zeros_like(band, dtype='u1')
    streched[band_mask] = temp_arr
    return streched





def create_truecolour(out_truecolor_name='tci.jpg', image_paths=None,
                      min_percentiles={}, max_percentiles={}, power_scales={}, nodata_value=0,
                      view=True
                      ):
    """
    Create a Landsat8 RGB image from three BANDS (red, green, and blue).
    Use custom stretching to enhance the output image

    :param out_truecolor_path: str, absolute path  or the RGB truecolor image
    :param image_paths: dict, band name, str:image path on local disk, str, absolute path
    :param min_percentiles: dict containing per band minimum percentiles to consider when stretching
            default value {'red': 1, 'green': 1, 'blue': 5}
    :param max_percentiles: dict containing per band maximum percentiles to consider when stretching
            default value {'red': 99, 'green': 99, 'blue': 99}
    :param power_scales: dict containing per band power scaling
    :param nodata_value: the value to ignore in bands when performing stretching
    :param view: bool, if True the RGB image will be displayed using pylab
    :return: a
    """

    logger.info(f'Computing true color image...')
    bands = list()
    for name, local_image_path in image_paths.items():
        local_folder, _ = os.path.split(local_image_path)
        with rasterio.open(local_image_path) as raster:
            if name == 'red':
                bounds = raster.bounds
                llbounds = transform_bounds(raster.crs, rasterio.crs.CRS.from_epsg(4326), *bounds)
            raw_band_data = raster.read().squeeze()
            min_perc = min_percentiles[name]
            max_perc = max_percentiles[name]
            power_scale = power_scales[name]
            logger.debug(f'Stretching band {name} with min_percentile {min_perc} max_percentile {max_perc} and power scale {power_scale}')
            streched_band_data = custom_stretch(band=raw_band_data,
                                                min_percentile=min_perc,
                                                max_percentile=max_perc,
                                                power_scale=power_scale,
                                                nodata_value=nodata_value)
            bands.append(streched_band_data)

    rgb = np.dstack(bands)
    out_truecolor_path = os.path.join(local_folder, out_truecolor_name)
    logger.info(f'Writing 8-bit true color image to {out_truecolor_path}')
    plt.imsave(out_truecolor_path, rgb)
    if view:
        import pylab
        pylab.imshow(rgb, interpolation='bilinear')
        pylab.title('rgb')
        pylab.show()
    return llbounds
def create_latlon_map(bounds=None, folder_to=None, map_file_name='map.jpg'):
    """
    Create a latlon map targeting Japan and containing the
    bounds as a rectangle
    :param bounds: iter of gfloat, the bounds in latlon projection
    :param map_path: str, path where to store teh map
    :return: None
    """
    proj = ccrs.PlateCarree()
    lon_min, lat_min, lon_max, lat_max = bounds
    pgon = Polygon(
                    ((lon_min, lat_min),
                    (lon_min, lat_max),
                    (lon_max, lat_max),
                    (lon_max, lat_min),
                    (lon_min, lat_min)),
                    transform=proj, facecolor='none', edgecolor='red',
                    zorder=3
                   )



    plt.figure(figsize=(8, 12))
    ax = plt.axes(projection=proj)
    ax.set_extent([128, 152, 30, 48], ccrs.PlateCarree())
    coast = cfeature.NaturalEarthFeature(category='physical', scale='50m',
                                facecolor='none', name='coastline', edgecolor='black')
    countries = cfeature.NaturalEarthFeature(category='physical', scale='50m',
                                         facecolor='lightgray', name='land', )
    ax.add_feature(coast)
    ax.add_feature(countries)
    ax.gridlines(draw_labels=True)
    #ax.add_geometries([pgon], crs=ccrs.PlateCarree(), facecolor='none', edgecolor='red', )

    ax.plot(139.839478, 35.652832, 'ro', markersize=3, transform=ccrs.Geodetic())
    ax.text(139, 36, 'Tokyo', transform=ccrs.Geodetic())
    ax.add_patch(pgon)
    plt.title('Landsat 8 true color image from \nLC08_L1TP_107035_20190105_20190130_01_T1_B{4,3,2}.tiff', y=1.08)
    map_path = os.path.join(folder_to, map_file_name)
    logger.info(f'Saving latlon map to {map_path}')
    plt.savefig(map_path,dpi=96)




if __name__ == '__main__':
    import argparse as ap

    logging.basicConfig()
    logger.setLevel('INFO')
    _, name = os.path.split(__file__)
    logger.name = name
    #handle args

    arg_parser = ap.ArgumentParser(formatter_class=ap.ArgumentDefaultsHelpFormatter)
    arg_parser.add_argument('-wf', '--working_folder', type=str,  required=True, help='Folder where the Landsat8 images will be downloaded', )
    arg_parser.add_argument('-minperc', '--min_percentiles', type=float, nargs='+', default = (1,1,5), help='Per band (red, green blue), percentiles to use when computing minimum value used to stretch the band', )
    arg_parser.add_argument('-maxperc', '--max_percentiles', help='Per band (red, green blue) percentiles to use when computing maximum value used to stretch the band', type=float, nargs='+', default = (99,99,99))
    arg_parser.add_argument('-pwr', '--power_scales', help='Per band (red, green blue) power scales', type=float, nargs='+', default = (1.1, 1.4, 2) )
    arg_parser.add_argument('-no_data', '--no_data', help='Background value to be ignored during stretching, common to all bands', type=int, default = 0 )
    arg_parser.add_argument('-v', '--view', help='visualize the RGB image using pylab', type=bool, default=False )

    #parse and collect args
    args = arg_parser.parse_args()
    band_names = list(landsat_truecolor_bands.keys())
    min_percentiles = dict(zip(band_names, args.min_percentiles))
    max_percentiles = dict(zip(band_names, args.max_percentiles))
    power_scales = dict(zip(band_names, args.power_scales))





    #compute urls
    image_urls = urls_from_bands(truecolor_bands=landsat_truecolor_bands)
    #fetch the image paths from disk or download them to folder_to if they do not exist in this folder
    image_paths = load_or_download(image_urls, folder_to=args.working_folder, chunked=True)

    #crate true color

    latlon_bounds = create_truecolour(image_paths=image_paths,
                      min_percentiles=min_percentiles,
                      max_percentiles=max_percentiles,
                      power_scales=power_scales,
                      nodata_value=args.no_data,
                      view=args.view)
    #create latlon map with the bounds
    create_latlon_map(folder_to=args.working_folder, bounds=latlon_bounds)



