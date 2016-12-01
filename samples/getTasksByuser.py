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

from optparse import OptionParser,make_option

import atexit
import sys
import datetime
from pyVim import connect
from pyVmomi import vmodl
from pyVmomi import vim
import argparse
import pyVmomi
import ssl

import textwrap
import time
import sys
import os
import pytz
from datetime import datetime, timedelta
"""
sample call
./taskListByUser.py --host 'host'  --user 'user' --password 'pwd' --port 443
"""
def GetArgs():
   """
   Supports the command-line arguments listed below.
   """
   parser = argparse.ArgumentParser(description='Process args for retrieving tasks')
   parser.add_argument('-s', '--host', required=True, action='store', help='Remote host to connect to')
   parser.add_argument('-o', '--port', default=443,   action='store', help='Port to connect on')
   parser.add_argument('-u', '--user', required=True, action='store', help='User name to use when connecting to host')
   parser.add_argument('-p', '--password', required=True, action='store', help='Password to use when connecting to host')
   args = parser.parse_args()
   return args


def main():
   """
   Simple command-line program for listing tasks with a timeframe for a user.
   """

   args = GetArgs()
   try:
      si = None

      ssl._create_default_https_context = ssl._create_unverified_context
      try:
         si = connect.SmartConnect(
            host  = args.host,
            user  = args.user,
            pwd   = args.password,
            port  = int(args.port)
         )
      except IOError, e:
        pass
      if not si:
         print "Could not connect to the specified host using given credentials %s %s  %s %s " %(args.host,args.user,args.password,args.port)
         return -1

      atexit.register(connect.Disconnect, si)
      
      content = si.RetrieveContent()
      taskManager = content.taskManager
      specByuser = vim.TaskFilterSpec.ByUsername(userList= args.user)
     
      tasks = taskManager.CreateCollectorForTasks(vim.TaskFilterSpec(userName=specByuser))
      
      tasks.ResetCollector()
      alltasks = tasks.ReadNextTasks(999)
      
      yesterday = datetime.now() - timedelta(1) # Get yesterday's time
      eastern = pytz.timezone('US/Eastern')
      for task in alltasks:
          if task.startTime >  eastern.localize(yesterday):
              print str(task.startTime) + ' ' + task.entityName + ' ' + task.state 
      print 'Destroying collector'
      tasks.DestroyCollector()

   except vmodl.MethodFault, e:
      print "Caught vmodl fault : " + e.msg
      return -1
   except Exception, e:
      print "Caught exception : " + str(e)
      return -1

   return 0

# Start program
if __name__ == "__main__":
   main()

