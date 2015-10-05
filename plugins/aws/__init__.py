import string
import boto
import json


def describe_environments(params):
    client = boto.connect_beanstalk()
    response = client.describe_environments()
    environments = response["DescribeEnvironmentsResponse"][
        "DescribeEnvironmentsResult"]["Environments"]
    print environments

    return json.dumps([environment["EnvironmentName"] for environment in environments])


def environment_health(params):
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


def environment_logs(params):
    if len(params) == 0:
        return "Usage: !logs environment_name"
    client = boto.connect_beanstalk()
    try:
        client.request_environment_info(environment_name=params[0])
        r = client.retrieve_environment_info(
            environment_name=params[0])
        environmentinfo = r[
            "RetrieveEnvironmentInfoResponse"][
            "RetrieveEnvironmentInfoResult"][
            "EnvironmentInfo"]
        if len(environmentinfo) > 0:
            response = environmentinfo[0]["Message"]
        else:
            response = "Generating logs.. request again in 10 seconds."

    except Exception as e:
        response = str(e.message).replace('"', "")
    return json.dumps(response)


functions = {
    'describe_environments': describe_environments,
    'logs': environment_logs,
    'health': environment_health
}


def do_command(command, params):
    return functions[command](params)


def do(args, pipe=None):
    arg = string.split(args)
    if len(arg) == 0:
        return "No arguments given"
    else:
        command = string.strip(arg[0])
        params = arg
        params.pop(params.index(command))
        return do_command(command, params)
