import time


def time_execution(func):
    def getruntime(*args):
        start = time.clock()
        result = func(*args)
        end = time.clock()
        print 'Run time of %s is %4.2fs' % (func.__name__, (end - start))
        return result

    return getruntime
