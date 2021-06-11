
import os
import sys
import subprocess
from urllib.parse import urlparse

import jenkins


def execute(command):
    ''' Execute a command with its parameters and return the exit code '''
    try:
        return subprocess.check_call([command], stderr=subprocess.STDOUT,shell=True)
    except subprocess.CalledProcessError as excp:
        return excp.returncode


def check_connectivity_ping(url):
    ''' Check if the script can access resources at IBM Cloud'''
    domain = urlparse(url).netloc
    server_ip = (domain.split(":")[0])
    print("INFO: Checking the Jenkins server availability...")
    tentative = 0
    for tentative in range(5):
        if execute("ping -c 1 " + server_ip) == 0:
            print("INFO: Jenkins is accessible...")
            return True
        elif tentative >= 5:
            print("ERROR: Jenkins is NOT accessible...")
            return False
        tentative += tentative


def get_jenkins_server_parameters():
    ''' Parameters to connect to a Jenkins server '''
    jenkins_server_parameters = {
        'POWERVS_JENKINS_URL': os.getenv("POWERVS_JENKINS_URL"),
        'POWERVS_JENKINS_USER': os.getenv("POWERVS_JENKINS_USER"),
        'POWERVS_JENKINS_TOKEN': os.getenv("POWERVS_JENKINS_TOKEN")
    }

    if not any([jenkins_server_parameters["POWERVS_JENKINS_URL"], jenkins_server_parameters["POWERVS_JENKINS_USER"], jenkins_server_parameters["POWERVS_JENKINS_TOKEN"]]):
        sys.exit("ERROR: The credentials to access the Jenkins server were not set.")

    return jenkins_server_parameters


def get_jenkins_job_parameters():
    ''' Parameters for executing a Jenkins job '''
    jenkins_job_parameters = {
        'BUILD_NAME_TO_COUNT': os.getenv("BUILD_NAME_TO_COUNT"),
    }
    return jenkins_job_parameters


def connect_to_jenkins():
    '''Check if Jenkins is ready to be used'''

    jenkins_url = get_jenkins_server_parameters()["POWERVS_JENKINS_URL"]
    jenkins_user = get_jenkins_server_parameters()["POWERVS_JENKINS_USER"]
    jenkins_token = get_jenkins_server_parameters()["POWERVS_JENKINS_TOKEN"]

    is_jenkins_available = False

    if not check_connectivity_ping(jenkins_url):
        print("ERROR: Could not reach " + jenkins_url)
        is_jenkins_available = False
    else:
        # connecting to the jenkins instance
        print("INFO: Connecting to the Jenkins instance...")
        jenkins_server = jenkins.Jenkins(jenkins_url, username=jenkins_user,
                                     password=jenkins_token, timeout=45)

        # collects the Jenkins version to indicate it is available
        user = jenkins_server.get_whoami()
        version = jenkins_server.get_version()

        if version:
            print('Hello %s from Jenkins %s' % (user['fullName'], version))
            is_jenkins_available = True
    return [is_jenkins_available,jenkins_server]


def action():
    ''' Execute the proper Jenkins action'''

    is_jenkins_available = connect_to_jenkins()
    if is_jenkins_available[0]:
        count = get_build_count(is_jenkins_available[1],get_jenkins_job_parameters()["BUILD_NAME_TO_COUNT"])
        print ("TOTAL:" + str(count))


def get_build_count(jenkins_server, build_name_to_count):
    ''' Get the number of running builds for a given job '''
    if build_name_to_count:
        builds = jenkins_server.get_running_builds()
        build_counter = 0
        print ("Counting the number of running builds for " + build_name_to_count + "...")
        for build in builds:
            # Why -3?
            # https://<Jenkins_URL>/job/ibmcloud-powervs-pool-of-clusters/job/monitor-and-fill-pull/357/
            # -1 is empty, -2 is 357 and -3 is what we need: monitor-and-fill-pull
            build_name = build['url'].rstrip().split("/")[-3]
            if build_name and build_name == build_name_to_count:
                build_counter += 1
    else:
        sys.exit("ERROR: env var BUILD_NAME_TO_COUNT was not set")
    return build_counter


def main():
    '''Calls the main execution function.'''
    action()


if __name__ == "__main__":
    sys.exit(main())
