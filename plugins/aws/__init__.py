import string
import boto
import json
from twisted.internet import reactor
import itertools


def describe_environments(params, coriolis):
    client = boto.connect_beanstalk()
    response = client.describe_environments()
    environments = response["DescribeEnvironmentsResponse"][
        "DescribeEnvironmentsResult"]["Environments"]
    print environments

    return str(json.dumps([environment["EnvironmentName"] for environment in environments]))


def environment_health(params, coriolis):
    try:
        client = boto.connect_beanstalk()
        if len(params) == 0:
            response = client.describe_environments()
        else:
            response = client.describe_environments(environment_names=params)
        environments = response["DescribeEnvironmentsResponse"][
            "DescribeEnvironmentsResult"]["Environments"]

        return json.dumps([{
            environment[
                "EnvironmentName"]: environment["Health"]} for environment in environments])
    except Exception as e:
        return e.message


def environment_logs(params, coriolis):

    if len(params) == 0:
        return "Usage: !logs environment_name"
    coriolis.msg(coriolis.current_chan, "Tailing logs..")
    client = boto.connect_beanstalk()
    tries = iter([x for x in xrange(2, 7)])  # 20 seconds
    timeout = next(tries)
    response = ""

    def _get_logs():
        try:
            delay = next(tries)
            client.request_environment_info(environment_name=params[0])
            r = client.retrieve_environment_info(
                environment_name=params[0])
            environmentinfo = r[
                "RetrieveEnvironmentInfoResponse"][
                "RetrieveEnvironmentInfoResult"][
                "EnvironmentInfo"]
            if len(environmentinfo) > 0:
                coriolis.msg(coriolis.current_chan, str(environmentinfo[0]["Message"]))
            else:
                coriolis.msg(coriolis.current_chan, "Tail not finished, Requesting again in %s seconds." % delay)
                reactor.callLater(delay, _get_logs)
        except StopIteration:
            coriolis.msg(coriolis.current_chan, "Couldn't get logs after 20 seconds, you should try again.")
        except boto.exception.BotoServerError as e:
            if "must be ready" in str(e.message.lower()):
                coriolis.msg(coriolis.current_chan, "waiting for aws..")
            else:
                coriolis.msg(coriolis.current_chan, str(e))
            reactor.callLater(delay, _get_logs)
    reactor.callLater(timeout, _get_logs)
    return ""


def show_help(params, coriolis):
    helptext = """
    \r\nAWS Plugin\r\n
    ===================\r\n
    Available commands are: \r\n
    """

    for k in [str(k) + "\r\n" for k in functions.keys()]:
        helptext += k
    return helptext


functions = {
    'describe_environments': describe_environments,
    'logs': environment_logs,
    'health': environment_health,
    'help': show_help
}


def do_command(command, params, coriolis):
    return functions[command](params, coriolis)


def do(args, coriolis=None):
    arg = string.split(args)
    if len(arg) == 0:
        return "No arguments given"
    else:
        command = string.strip(arg[0])
        params = arg
        params.pop(params.index(command))
        return do_command(command, params, coriolis)
