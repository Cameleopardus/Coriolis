import string
def show_help(params, coriolis):
    return "lol, did you expect something useful?"


def proc_comm(params, coriolis):
    if not coriolis:
        return "not initialized."
    else:
        coriolis.msg(coriolis.current_chan, "sending data..")
        coriolis.msg(coriolis.current_chan, 'moar...')
        return "done."

functions = {
    'help': show_help,
    'proc_comm': proc_comm
}


def do_command(command, params, coriolis):
    if coriolis:
        return functions[command](params, coriolis)
    else:
        return functions[command](params)


def do(args, coriolis=None):
    arg = string.split(args)
    if len(arg) == 0:
        return "No arguments given"
    else:
        command = string.strip(arg[0])
        params = arg
        params.pop(params.index(command))
        return do_command(command, params, coriolis)
