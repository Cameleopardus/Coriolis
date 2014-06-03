


def do(args, pipe=None):
    r = ''.join(format(ord(x), 'b') for x in args)
    return r