#Landsat 8 truecolor 8-bit composite creator

Uses a specific landsat image from landsat8 amazon cloud source to
create an 8-bit true color composite (bands 4 3 and 2).
Uses custom stretchng to enhance visually the output image

#Download
git clone https://github.com/jferencik/landsatrgb.git .

#Installation
1. install docker. Folow your OS instructions from
    https://docs.docker.com/install/

2. use the dockerfile to build an image

    docker build -t landsat_tc .

#Usage

3. run the script




```bash
docker run --rm -v $(pwd):/app landsat_tc python3 /app/solution.py -f
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

# Create true color composites
create a low contrast blueish composite
```bash
docker run --rm -v $(pwd):/app landsat_tc python3 /app/solution.py -wf /app -p 2 2 2 -minperc 5 5 5
```

create a high contrast true color]

```bash
docker run --rm -v $(pwd):/app landsat_tc python3 /app/solution.py -wf /app -p 2 2 2 -minperc 1 1 5
```