from IPython.core.debugger import Tracer
from player import Player
import os
import sys
import scipy.io as sio
import numpy as np
import cPickle as pickle

def showResults(data, schedule, results):

  players_np = np.array(data)
  scores_np = np.array(results['scores'][0])
  results_selection = results['x']
  days = results['days'][0][0]
  start_index = results['start_index'][0][0]
  curr_team = players_np[np.nonzero(results['curr_team'][0])].tolist()
  curr_team_mask = results['curr_team'][0]
  for index in xrange(days):
    team_players = players_np[np.nonzero(results_selection[index])].tolist()
    team_player_scores = scores_np[np.nonzero(results_selection[index])].tolist()
    if index == 0:
      coming_in = [int(x < 0) for x in [x-y for x,y in zip(curr_team_mask, results_selection[index])]]

      going_out = [int(x > 0) for x in [x-y for x,y in zip(curr_team_mask, results_selection[index])]]
    else:
      going_out = [int(x < 0) for x in [x-y for x,y in zip(results_selection[index], results_selection[index-1])]]
      coming_in = [int(x > 0) for x in [x-y for x,y in zip(results_selection[index], results_selection[index-1])]]
    print "These players leaving:\n {0}".format(players_np[np.nonzero(going_out)].tolist())
    print "These players coming in:\n {0}".format(players_np[np.nonzero(coming_in)].tolist())
    print schedule['schedule'][index+start_index]
    print team_player_scores
    print team_players
    # Tracer()()
    print "\n\n\n"
  Tracer()()

def main():
  if len(sys.argv) <= 2:
    print "Run as pickTeam.py <data pickle file name> <schedule pickle file name> <results mat file>"
    sys.exit()
  file_to_parse = sys.argv[1]
  file2_to_parse = sys.argv[2]
  file3_to_parse = sys.argv[3]
  if not os.path.isfile(file_to_parse):
    print "{0} does not exist.".format(file_to_parse)
    sys.exit()
  if not os.path.isfile(file2_to_parse):
    print "{0} does not exist.".format(file2_to_parse)
    sys.exit()
  if not os.path.isfile(file3_to_parse):
    print "{0} does not exist.".format(file3_to_parse)
    sys.exit()
  f = open(file_to_parse)
  global data
  data = pickle.load(f)
  f.close()
  g = open(file2_to_parse)
  schedule = pickle.load(g)
  g.close()
  h = open(file3_to_parse)
  results = sio.loadmat(h)
  h.close()
  showResults(data, schedule, results)


if __name__ == '__main__':
  main()
