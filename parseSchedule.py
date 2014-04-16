import sys
import os
import cPickle as pickle
from IPython.core.debugger import Tracer



def parseSchedule(data):
  matches = data.split('\n')[:-1]
  matches = [match.split(',') for match in matches]
  cluster_matches = {}
  for match in matches:
    if not match[3] in cluster_matches:
      cluster_matches[match[3]] = []
    cluster_matches[match[3]].extend([match[1].strip(),match[2].strip()])
  final_schedule = sorted(cluster_matches.iteritems(), key=lambda x:x[0])
  sched = {}
  sched["schedule"] = final_schedule
  sched["matches"] = len(matches)
  return sched


def main():
  if len(sys.argv) <= 1:
    print "Run as parseSchedule.py <csv of schedule>"
    sys.exit()
  file_to_parse = sys.argv[1]
  if not os.path.isfile(file_to_parse):
    print "{0} does not exist.".format(file_to_parse)
    sys.exit()
  f = open(file_to_parse)
  data = f.read()
  schedule = parseSchedule(data)
  print "Writing schedule to Schedule-2014.pik"
  pickle.dump(schedule, open("Schedule-2014.pik", "wb"))
  f.close()

if __name__ == '__main__':
  main()



