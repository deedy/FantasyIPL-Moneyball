from urllib2 import Request, urlopen, URLError
from IPython.core.debugger import Tracer
from bs4 import BeautifulSoup
from bs4 import SoupStrainer
import cPickle as pickle
import os
import re
import time
import sys
from player import Player




def main():
  if len(sys.argv) <= 1:
    print "Run as fixbug.py <data pickle file name>"
    sys.exit()
  file_to_parse = sys.argv[1]
  if not os.path.isfile(file_to_parse):
    print "{0} does not exist.".format(file_to_parse)
    sys.exit()
  f = open(file_to_parse)
  data = pickle.load(f)
  new_player_list = []
  for player in data:
      if player.name == "Francois du Plessis":
        name_to_use = "Faf du Plessis"
      elif player.name == "Jaidev Unadkat":
        name_to_use = "Jaydev Unadkat"
      else:
        name_to_use = player.name


      file_to_write = "Data-Rich/player-"+name_to_use.replace(" ","-")
      if "battingStats" in player.tournamentStats["international"]:
        statfixing = player.tournamentStats["international"]["bowlingStats"][0]
        if not statfixing['b'] == 0.0:
            # print statfixing
            # balls = round((statfixing['b'] % 1)/0.1)
            # overs = round(statfixing['b'] - balls/10)
            # statfixing['b'] = overs*6  + balls
            # statfixing['e'] = 6*statfixing['r']/statfixing['b']
            # if not statfixing['w'] == 0.0:
            #     statfixing['sr'] = statfixing['b']/statfixing['w']
            # print statfixing
            # # Tracer()()
            statfixing['b'] = statfixing['b']/6
            statfixing['e'] = 6*statfixing['r']/statfixing['b']
            if not statfixing['w'] == 0.0:
                statfixing['sr'] = statfixing['b']/statfixing['w']
            print statfixing
            # Tracer()()


      pickle.dump(player, open(file_to_write, "wb" ))
  print "complete dump"
  pickle.dump(data, open("IPL-Complete-Stats-2.pik", "wb" ))
  f.close()

if __name__ == '__main__':
  main()

