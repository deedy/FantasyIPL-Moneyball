import os
import sys
import re
import json
import matplotlib.pyplot as plt
import cPickle as pickle
import backtest_pickteam
import backtest_results
from pymatbridge import Matlab
from IPython.core.debugger import Tracer
# def findteamsplayed(time_data):
#   for stamp in time_data

def getPlayer(players, substr):
  return filter(lambda x: substr in x.name.lower(), players)

def convertToPlayersTimeData(time_data, data):
  time_data2 = []
  for date in time_data:
    points_for_stamp = {}
    for pname in date[1]:
      player = getPlayer(data, pname)
      if len(player) < 1:
        # print pname
        continue
      points_for_stamp[player[0]] = date[1][pname]
    time_data2.append((date[0],points_for_stamp))
  return time_data2

def backtest(filename, data, schedule_data):
  f = open(filename)
  f.readline()
  player_data = {}
  time_data = []
  for i in xrange(50):
    line = f.readline()
    if line is None or len(line) == 0:
      break
    date = int(line[:3])
    print date
    jsonvalue = "{"+f.readline()+"}"
    value = json.loads(jsonvalue)
    time_data.insert(0,(date,value))
    for p in value:
      if not p in player_data:
        player_data[p] = [0]
      player_data[p].insert(0,value[p])

  time_data2 = convertToPlayersTimeData(time_data, data)

  teams = set([i.team for i in data])

  for i in xrange(len(time_data2)):
    stamp_data = time_data2[i][1]
  Tracer()()
  portfolio = ["rohit sharma", "ajinkya rahane", "david warner", "glenn maxwell", "robin uthappa", "shane watson", "sandeep sharma", "sunil narine", "pravin tambe", "yuzvendra chahal", "bhuvneshwar kumar"]
  # portfolio = ["yuzvendra chahal", "shakib al hasan", "shane watson", "rohit sharma", "sandeep sharma", "sunil narine", "ajinkya rahane", "jacques kallis", "robin uthappa", "jayant yadav","bhuvneshwar kumar"]
  # portfolio = ["manish pandey", "rohit sharma","jacques kallis","robin uthappa", "aditya tare", "ambati rayudu", "morne morkel","piyush chawla","sunil narine","lasith malinga","pragyan ojha"]
  power_player = "glenn maxwell"
  # power_player = "bhuvneshwar kumar"
  portfolio_p = set([getPlayer(data, p)[0] for p in portfolio])
  power_player_p = getPlayer(data, power_player)[0]
  points = 0
  subs = 75

  mlab = Matlab(matlab='/Applications/MATLAB_R2013a.app/bin/matlab')
  mlab.start()
  for i in xrange(4,len(time_data2)):
    # START = str(time_data2[i][0])
    # CURRENT_TEAM = set(portfolio)
    # SUBSTITUTIONS = subs
    # PAST_STATS = time_data[i][1]
    print "\n\n\n\n\n\n"
    print (subs, str(time_data2[i][0]))
    print set(portfolio_p)
    print points
    print "\n\n\n\n\n\n"
    # print time_data[i-1][1]
    # Tracer()()

    inp = (subs, str(time_data2[i][0]), set(portfolio), time_data[i-1][1])
    backtest_pickteam.pickTeam(data, schedule_data, inp)



    res = mlab.run_func('/Users/deedy/Dev/FantasyIPL-Moneyball/python2matlab.m', {}, maxtime = 500)
    changes = backtest_results.getResults(data, schedule_data, res['result'])
    subs -= changes[2]
    portfolio_p = changes[0]
    power_player_p = changes[1]
    # Tracer()()
    # update portfolio
    # update subs
    # update power player
    # Tracer()()

    teams = [(p,time_data2[i][1][p] - time_data2[i-1][1][p] ) for p in time_data2[i][1] if p in portfolio_p]
    print teams
    pthis = 0
    for i in teams:
      if power_player_p == i[0]:
        pthis += 2*i[1]
      else:
        pthis += i[1]
    points+= pthis
    print "{0}\t{1}\t{2}\n\n".format(points, pthis, subs)


    # print "{0}\t{1}".format(time_data2[i][0] , teams)

  mlab.stop()
  Tracer()()
  f.close()


def main():
  file_to_parse = 'historical-past-stats-2.txt'
  data_file = 'IPL-Complete-Stats-2.pik'
  schedule_file = 'Schedule-2014.pik'
  f = open(schedule_file)
  schedule_data = pickle.load(f)
  f.close()
  f = open(data_file)
  data = pickle.load(f)
  f.close()
  backtest(file_to_parse, data, schedule_data)

if __name__ == '__main__':
  main()
