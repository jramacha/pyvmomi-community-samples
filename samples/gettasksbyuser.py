#!/usr/bin/env python
"""

Written by Jayanth Ramachandran
Github: https://github.com/jramacha
Email: sqljay.ram@gmail.com
Note: Example code For testing purposes only

This code has been released under the terms of the Apache-2.0 license
http://opensource.org/licenses/Apache-2.0

A simple program for listing recent vCenter tasks for a particular user within the last 24 hours.

"""

import atexit
import sys
import datetime
from pyVim import connect
from pyVmomi import vmodl
from pyVmomi import vim
import argparse
import pyVmomi
import ssl

import pytz
from datetime import datetime, timedelta

def get_args():
    """
    Supports the command-line arguments listed below.
    """
    parser = argparse.ArgumentParser(description=\
						'Process args for retrieving all the Virtual Machines')
    parser.add_argument('-s', '--host', required=True, action='store', \
						help='Remote host to connect to')
    parser.add_argument('-o', '--port', default=443, action='store', \
						help='Port to connect on')
    parser.add_argument('-u', '--user', required=True, action='store', \
						help='User name to use when connecting to host')
    parser.add_argument('-p', '--password', required=True, \
						action='store', help='Password to use when connecting to host')
    args = parser.parse_args()
    return args


def main():
    """
    Simple command-line program for listing tasks .
    """

    args = get_args()
    try:
        service_instance = None
        ssl._create_default_https_context = ssl._create_unverified_context
        try:
            service_instance = connect.SmartConnect(
            host=args.host,
            user=args.user,
            pwd=args.password,
            port=int(args.port)
           )
        except IOError as e_x:
            pass
        if not service_instance:
            print "Could not connect to the specified host" \
					"uservice_instanceng given credentials \
					%s %s  %s %s " %(args.host, args.user, args.password, args.port)
            return -1

        atexit.register(connect.Disconnect, service_instance)
        content = service_instance.RetrieveContent()
        task_manager = content.taskManager
        spec_byuser = vim.TaskFilterSpec.ByUsername(userList=args.user)
        tasks = task_manager.CreateCollectorForTasks\
				(vim.TaskFilterSpec(userName=spec_byuser))
        tasks.ResetCollector()
        alltasks = tasks.ReadNextTasks(999)
        yesterday = datetime.now() - timedelta(1) # Get yesterday's time
        eastern = pytz.timezone('US/Eastern')
        for task in alltasks:
            if task.startTime > eastern.localize(yesterday):
                print str(task.startTime) + ' ' + task.entityName + \
								 ' ' + task.state + ' ' + task.descriptionId
        print 'Destroying collector'
        tasks.DestroyCollector()

    except vmodl.MethodFault as e_x:
        print "Caught vmodl fault : " + e_x.msg
        return -1
    except Exception as e_x:
        print "Caught exception : " + str(e_x)
        return -1

    return 0

# Start program
if __name__ == "__main__":
    main()
