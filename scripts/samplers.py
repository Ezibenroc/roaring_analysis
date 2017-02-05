import random
from utils import error

class DiscreteSampler:
    def __init__(self, values):
        assert len(values) > 0
        self.values = values

    def __str__(self):
        return '%s(%s)' % (self.__class__.__name__, self.values)

    def sample(self):
        self.last_sampled = random.choice(self.values)
        return self.last_sampled

    def min(self):
        if type(self.values) == range: # min function iterate on all the values...
            return self.values.start
        else:
            return min(self.values)

    def max(self):
        if type(self.values) == range: # min function iterate on all the values...
            return self.values.stop-1
        else:
            return max(self.values)

class ContinuousSampler:
    def __init__(self, start, stop):
        assert start <= stop
        self.start = start
        self.stop = stop

    def __str__(self):
        return '%s(%s, %s)' % (self.__class__.__name__, self.start, self.stop)

    def sample(self):
        self.last_sampled = random.random()*(self.stop-self.start)+self.start
        return self.last_sampled

    def min(self):
        return self.start

    def max(self):
        return self.stop

class CopySampler:
    def __init__(self, original):
        self.original = original

    def __str__(self):
        return '%s(%s)' % (self.__class__.__name__, self.original)

    def sample(self):
        return self.original.last_sampled

    def min(self):
        return self.original.min()

    def max(self):
        return self.original.max()

LIST_SEP  = ','
RANGE_SEP = ':'

def parse_sample(string, number_cls):
    if RANGE_SEP in string:
        if LIST_SEP in string:
            error('Cannot mix ranges and lists. Got %s.' % string)
        start, stop = parse_range(string, number_cls)
        if number_cls is int:
            return DiscreteSampler(range(start, stop+1))
        else:
            assert number_cls is float
            return ContinuousSampler(start, stop)
    else:
        return DiscreteSampler(parse_list(string, number_cls))

def parse_list(string, number_cls):
    splitted = string.split(LIST_SEP)
    return [parse_number(x, number_cls) for x in splitted]

def parse_range(string, number_cls):
    splitted = string.split(RANGE_SEP)
    if len(splitted) > 2:
        error('Incorrect value for range, got %s.' % string)
    elif len(splitted) == 1:
        value = parse_number(splitted[0], number_cls)
        result = (value, value)
    else:
        result = (parse_number(splitted[0], number_cls), parse_number(splitted[1], number_cls))
    if result[1] < result[0]:
        error('Empty range, got %s.' % string)
    return result

def parse_number(string, number_cls):
    try:
        result = number_cls(string)
    except ValueError:
        error('Incorrect value for %s, got %s.' % (number_cls.__name__, string))
    return result

def check_params(size, density):
    if density.max() > 1 or density.min() <= 0:
        error('Density must be in ]0, 1], got density=%s.' % (density,))
    if size.min() <= 0:
        error('Size must be positive, got size=%s.' % (size,))
    if size.max()/density.min() >= 2**32:
        error('This size/density combination will yield to non 32 bits integers, got size=%s and density=%s.' % (size, density))
