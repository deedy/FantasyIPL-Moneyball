from IPython.core.debugger import Tracer
from player import Player
import os
import sys
import scipy.io as sio
import numpy as np
import cPickle as pickle

def showResults(data, schedule, results):
  # Tracer()()
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
    # Tracer()()

    powerplayer = [team_players[j] for j in xrange(len(team_players)) if team_player_scores[j] == min(team_player_scores)]
    powerplayer = powerplayer[0]
    subs = results['nextsubs'][0][0]
    return (team_players, powerplayer, subs)


def getResults(data, schedule, file3_to_parse):
  if not os.path.isfile(file3_to_parse):
    print "{0} does not exist.".format(file3_to_parse)
    sys.exit()
  h = open(file3_to_parse)
  results = sio.loadmat(h)
  h.close()
  return showResults(data, schedule, results)


