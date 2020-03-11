import unittest
import solution
from urllib.request import urlopen
import os

import rasterio
class CoreTest(unittest.TestCase):

    def setUp(self) -> None:
        self.bands_dict = solution.landsat_truecolor_bands
        self.working_folder = '/tmp'
        self.red_image = None

    def test_local_folder(self):
        assert os.path.isabs(self.working_folder), f'self.working_folder={self.working_folder} is not an absolute path'
        assert os.path.exists(self.working_folder), f'self.working_folder={self.working_folder} does not exist'
        assert os.access(self.working_folder, os.W_OK), f'self.working_folder={self.working_folder} is not writable'
    def test_create_urls(self):
        urls = solution.urls_from_bands(self.bands_dict)
        assert isinstance(urls, dict)

    def test_urls_exist(self):
        urls = solution.urls_from_bands(self.bands_dict)
        assert isinstance(urls, dict)
        for n, url in urls.items():
            with urlopen(url) as ourl:
                assert ourl.getcode() == 200

    def test_download_red_image(self):

        urls = solution.urls_from_bands(self.bands_dict)
        red_image_url = urls['red']
        root_url, image_name = os.path.split(red_image_url)
        local_image_path = os.path.join(self.working_folder, image_name)
        if not os.path.exists(local_image_path):
            with open(local_image_path, 'wb') as local_image:
                with urlopen(red_image_url) as response:
                    local_image.write(response.read())
        self.red_image = local_image_path


    def test_redimage_stretch(self):
        import numpy as np
        if self.red_image is not None:
            with rasterio.open(self.red_image) as raster:
                raw_band_data = raster.read().squeeze()
                stretched_red_image = solution.custom_stretch(band=raw_band_data,
                                                              min_percentile=1,
                                                              max_percentile=99,
                                                              power_scale=2
                )
                assert hasattr(stretched_red_image, '__array_interface__')
                assert stretched_red_image.dtype == np.uint8






if __name__ == '__main__':
    unittest.main()
