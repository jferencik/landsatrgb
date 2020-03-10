from functools import wraps
import datetime
def measure(func):
    @wraps(func)
    def _time_it(*args, **kwargs):
        start = datetime.datetime.now()
        try:
            return func(*args, **kwargs)
        finally:
            end = datetime.datetime.now()
            dur = end-start
            print(f'{func.__name__} total execution time: {dur}')
    return _time_it



def scale(arr_in, new_min=0., new_max=1., nstd=0):
    """
        Scale an array either in a new range or based on standard deviation
        If nstd is supplied and >0 the scaling will be based on standard deviation or difference from the mean value
        @args:
            @arr_in, numpy array to be scaled
            @new_min, float, the minimum of the new range, defaults ot 0
            @new_max, float, the minimum of the new range, defaults to 1
            @nstd, boolean, lag indicating that a standard deviation approach will be used to rescale the data. Also
            the value od nstd is multiplied with the standard deviation when computing the new range
    """
    old_min = arr_in.min()
    old_max = arr_in.max()
    if nstd:
        std = arr_in.std()
        mean = arr_in.mean()
        new_min = mean - nstd * std
        new_max = mean + nstd * std
    return ( (arr_in - old_min) / float(old_max - old_min)) * (new_max - new_min) + new_min
