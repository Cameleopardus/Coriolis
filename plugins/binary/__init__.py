
helptext = "Binary - turn strings into binary."
def do(args, coriolis=None):
    r = ''.join(format(ord(x), 'b') for x in args)
    return r
