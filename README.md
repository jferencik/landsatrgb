# Landsat 8 truecolor 8-bit composite creator

Uses a specific landsat image from landsat8 amazon cloud source to
create an 8-bit true color composite (bands 4 3 and 2).
Uses custom stretching to enhance visually the output image

# Download
git clone https://github.com/jferencik/landsatrgb.git .

# Installation
1. install docker. Folow your OS instructions from
    https://docs.docker.com/install/

2. use the dockerfile to build an image

    docker build -t landsat_tc .
 
3. run tests (optionally)
    There are two test modules, for core functionality and for run  functionality.
    The test modules needs the path to a folder where they can write. This path needs to be
    passed in when running the unittests like this:
    
    ```bash
        docker run --rm -v $(pwd):/landsat -e working_folder=/tmp landsattc python3 -m unittest discover -s /landsat
    ```
        
    

# Usage

1. check script command line options/capabilities
```bash
docker run --rm -v $(pwd):/landsat landsattc python3 /landsat/solution.py -h
```

```
usage: solution.py [-h] -wf WORKING_FOLDER
                   [-minperc MIN_PERCENTILES [MIN_PERCENTILES ...]]
                   [-maxperc MAX_PERCENTILES [MAX_PERCENTILES ...]]
                   [-pwr POWER_SCALES [POWER_SCALES ...]] [-no_data NO_DATA]
                   [-v VIEW]

optional arguments:
  -h, --help            show this help message and exit
  -wf WORKING_FOLDER, --working_folder WORKING_FOLDER
                        Folder where the Landsat8 images will be downloaded
                        (default: None)
  -minperc MIN_PERCENTILES [MIN_PERCENTILES ...], --min_percentiles MIN_PERCENTILES [MIN_PERCENTILES ...]
                        Per band (red, green blue), percentiles to use when
                        computing minimum value used to stretch the band
                        (default: (1, 1, 5))
  -maxperc MAX_PERCENTILES [MAX_PERCENTILES ...], --max_percentiles MAX_PERCENTILES [MAX_PERCENTILES ...]
                        Per band (red, green blue) percentiles to use when
                        computing maximum value used to stretch the band
                        (default: (99, 99, 99))
  -pwr POWER_SCALES [POWER_SCALES ...], --power_scales POWER_SCALES [POWER_SCALES ...]
                        Per band (red, green blue) power scales (default:
                        (1.1, 1.4, 2))
  -no_data NO_DATA, --no_data NO_DATA
                        Background value to be ignored during stretching,
                        common to all bands (default: 0)
  -v VIEW, --view VIEW  visualize the RGB image using pylab (default: False)

```

The script features two types of options that control how the bands are stretched. 
The percentiles, both min nad max aim at controlling
 the amount of  red blue respectively green color the true color  image will contain. For example to increase the amount of blue in
 the image  use equal power scales and minperc and lower the maxperc for the blue band:
 
 ```
docker run --rm -v $(pwd):/landsat landsattc python3 /landsat/solution.py -wf /landsat/data -pwr 2 2 2 -maxperc 98 98 95 -minperc 1 1 1
 ```
this will create a blueish image

The second option is the power scaling. Use this option to control the luminosity of the  true color image.
For example to create a very light image and thus decrese the contrast between adjacent pixels use a higer value for 
power scaling like 5 for all bands:

```bash
    docker run --rm -v $(pwd):/landsat landsattc python3 /landsat/solution.py -wf /landsat/data -pwr 5 5 5
```

# Create various true color composites




run with default settings or low contract true color:
```bash
docker run --rm -v $(pwd):/landsat landsattc python3 /landsat/solution.py -wf /landsat/data
```

create a high contrast true color which I prefer:

```bash
docker run --rm -v $(pwd):/landsat landsattc python3 /landsat/solution.py -wf /landsat/data -pwr 2 2 2
```

Fell free to test various options like setting different min and max percentiles per band  or using
different per band power scales.