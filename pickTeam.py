from IPython.core.debugger import Tracer
from player import Player
import cPickle as pickle
import os
import sys
import re
import math
import numpy as np
import scipy
from cvxopt import matrix
from cvxopt.solvers import qp
from cvxopt.solvers import conelp
import scipy.io as sio

global data
# Update num subs left
# Update start date
# Run current team setup
# Run past stas

SUBSTITUTIONS = 45
# DAYS = 37
START = "424"
# RUN IN SELECTION https://fantasy.iplt20.com/ifl/player/createteam
# var team = []
# $('#selectmyplayers').find('.playerlist').find('.namesorting').each(function(i,e) {team.push($(e).text().toLowerCase());});
# team
CURRENT_TEAM = set(["manish pandey", "ajinkya rahane", "dwayne smith", "francois du plessis", "suresh raina", "brendon mccullum", "akshar patel", "shane watson", "yuvraj singh", "ravichandran ashwin", "yuzvendra chahal"])
# RUN IN https://fantasy.iplt20.com/ifl/research/player_researchall
# var playerpoint = "";
# $('#selectplayersList').find('.playerlistouter').each(function(i,e) {playerpoint+="\""+$(e).find('.namesorting').text().toLowerCase()+"\":"+$(e).find('.pricesorting').text()+","});
# playerpoint
PAST_STATS = {"glenn maxwell":659,"jp duminy":318,"dwayne smith":310,"ravindra jadeja":299,"david miller":269,"rajat bhatia":236,"sunil narine":235,"lakshmipathy balaji":229,"ravichandran ashwin":221,"suresh raina":216,"akshar patel":213,"dhawal kulkarni":209,"yuzvendra chahal":209,"parthiv patel":202,"jacques kallis":200,"manish pandey":183,"ishwar pandey":181,"lasith malinga":180,"bhuvneshwar kumar":178,"varun aaron":166,"brendon mccullum":164,"ajinkya rahane":161,"stuart binny":153,"mitchell johnson":149,"ms dhoni":148,"jaidev unadkat":144,"kane richardson":144,"zaheer khan":142,"mitchell starc":137,"morne morkel":136,"dinesh karthik":135,"yuvraj singh":135,"cheteshwar pujara":131,"sanju samson":130,"shane watson":130,"robin uthappa":126,"mohammed shami":119,"pravin tambe":117,"amit mishra":117,"shakib al hasan":115,"dale steyn":114,"ambati rayudu":109,"ben hilfenhaus":104,"virender sehwag":104,"virat kohli":99,"francois du plessis":98,"albie morkel":92,"ross taylor":91,"piyush chawla":88,"steve smith":87,"mohit sharma":86,"nathan coulter-nile":85,"ab de villiers":84,"george bailey":76,"harbhajan singh":76,"jimmy neesham":75,"darren sammy":74,"ashok dinda":73,"lokesh rahul":73,"james faulkner":69,"rohit sharma":65,"david warner":63,"shikhar dhawan":63,"mayank agarwal":62,"rishi dhawan":57,"sandeep sharma":55,"parvinder awana":52,"mithun manhas":51,"abhishek nayar":51,"karn sharma":48,"murali vijay":44,"aditya tare":44,"aaron finch":44,"venugopal rao":43,"ishant sharma":43,"shahbaz nadeem":42,"suryakumar yadav":39,"nic maddinson":38,"yusuf pathan":33,"ashish nehra":32,"tim southee":32,"sachin rana":30,"wriddhiman saha":26,"wayne parnell":25,"vinay kumar":24,"corey anderson":22,"rahul sharma":19,"dwayne bravo":15,"murali kartik":15,"jasprit bumrah":13,"michael hussey":10,"brad hodge":9,"pragyan ojha":8,"manoj tiwary":7,"cm gautam":7,"kieron pollard":6,"john hastings":0,"vijay shankar":0,"baba aparajith":0,"ronit more":0,"samuel badree":0,"matt henry":0,"jayant yadav":0,"saurabh tiwary":0,"kedar jadhav":0,"milind kumar":0,"kevin pietersen":0,"laxmi ratan shukla":0,"quinton de kock":0,"siddarth kaul":0,"rahul shukla":0,"hs sharath":0,"shaun marsh":0,"gurkeerat mann singh":0,"mandeep singh":0,"shivam sharma":0,"manan vohra":0,"thisara perera":0,"beuran hendricks":0,"anureet singh":0,"shardul thakur":0,"karanveer singh":0,"chris lynn":0,"debabrata das":0,"andre russell":0,"kuldeep yadav":0,"ryan ten doeschate":0,"manvinder bisla":0,"veer pratap singh":0,"umesh yadav":0,"sayan mondal":0,"pat cummins":0,"jalaj saxena":0,"apporv wankhade":0,"ben dunk":0,"sushant marathe":0,"josh hazlewood":0,"krishmar santokie":0,"marchant de lange":0,"pawan suyal":0,"shreyas gopal":0,"unmukt chand":0,"karun nair":0,"ben cutting":0,"ankush bains":0,"dishant yagnik":0,"ankit sharma":0,"kevon cooper":0,"iqbal abdulla":0,"rahul tewatia":0,"deepak hooda":0,"vikramjeet malik":0,"a mishra":0,"vijay zol":0,"tanmay mishra":0,"chris gayle":0,"yogesh takawale":0,"shadab jakati":0,"abu nechim":0,"harshal patel":0,"ravi rampaul":0,"sandeep warrier":0,"muttiah muralitharan":0,"manpreet juneja":0,"ricky bhui":0,"srikkanth anirudha":0,"moises henriques":0,"naman ojha":0,"brendan taylor":0,"amit paunikar":0,"parveez rasool":0,"jason holder":0,"chama milind":0,"prasanth parameswaran":0,"ashish reddy":0,"pawan negi":-5,"irfan pathan":-6,"gautam gambhir":-17}
def getPlayer(players, substr):
  return filter(lambda x: substr in x.name.lower(), players)

def setUpAndSaveVars(players, scores, schedule):
  numplayers = len(players)

  # A and B
  team_total_constraint = [1.0]*numplayers
  wicketkeeper_constraint = [float(player.is_keeper) for player in players]
  A = matrix([team_total_constraint, wicketkeeper_constraint])
  A = A.trans()
  B = matrix([11.0, 1.0])

  # G and H
  all_unstrict_constraints = []
  all_unstrict_constraints_limits = []
  teams = set([player.team for player in players])
  teams = list(teams)



  for team in teams:
    all_unstrict_constraints.append([float(player.team == team) for player in players])
    all_unstrict_constraints_limits.append(6.0)


  batsman_constraint = [-float(player.is_batsman) for player in players]
  allrounder_constraint = [-float(player.is_allrounder) for player in players]
  uncapped_constraint = [-float(player.is_uncapped) for player in players]
  bowler_constraint = [-float(player.is_bowler) for player in players]
  bowling_constraint = [-float(player.is_bowler or player.is_allrounder) for player in players]
  overseas_constraint = [float(player.is_overseas) for player in players]
  price_constraint = [float(player.price)/1000000.0 for player in players]
  all_unstrict_constraints.extend([batsman_constraint, allrounder_constraint, uncapped_constraint, bowler_constraint, bowling_constraint, overseas_constraint, price_constraint])
  all_unstrict_constraints_limits.extend([-4.0, -1.0, -1.0, -2.0, -5.0, 4.0, 10.0])
  G = matrix(all_unstrict_constraints)
  G = G.trans()
  H = matrix(all_unstrict_constraints_limits)

  # P and Q
  Q = [-score for score in scores]

  # find_naive_one_time_best_team(Q,A,B,G,H)
  # Tracer()()

  Q_new = []

  days = len(schedule["schedule"])
  start_index = schedule["schedule"].index([x for x in schedule["schedule"] if x[0] == START][0])
  past_games = {}
  for t in teams:
    past_games[t] = 0
  for day in schedule["schedule"][:start_index]:
    for t in day[1]:
      past_games[t] += 1

  ## PAST SQUADS
  curr_team_indices = []
  for player_name in PAST_STATS:
    hscore = PAST_STATS[player_name]
    player_arr = getPlayer(players, player_name)
    if len(player_arr) > 1:
      print "Too many people with name {0}".format(player_name)
      Tracer()()
    elif len(player_arr) == 0:
      print "Name not found - {0}".format(player_name)
      Tracer()()
    else:
      player = player_arr[0]
      player_ind = players.index(player)
      if past_games[player.team] > 0:
        # print player
        # print Q[player_ind]
        weight_to_ipl = 0.2 + 0.8*(past_games[player.team]/14.0)
        Q[player_ind] = Q[player_ind]*(1-weight_to_ipl) + weight_to_ipl*(-hscore)/past_games[player.team]
        if hscore == 0:
          Q[player_ind] *= 0.5
        # print Q[player_ind]
        # print "\n\n"
        # Tracer()()
  scores = [-x for x in Q]

  ##
  print sorted(zip(players,Q), key=lambda x: -x[1])

  Tracer()()
  days = len(schedule["schedule"][start_index:])
  for day in schedule["schedule"][start_index:]:
    match_mask = [0]*len(all_unstrict_constraints[0])
    for playing_team in day[1]:
      match_mask = [sum(x) for x in zip(match_mask,all_unstrict_constraints[teams.index(playing_team)])]
    # Tracer()()
    ##### Kevin Pietersen ruled out for 417
    if day[0] == '417':
      ind = players.index(getPlayer(players, "kevin pietersen")[0])
      match_mask[ind] = 0
    ####

    Q_new.extend([a*b for a,b in zip(Q,match_mask)])
  Q_new = matrix(Q_new).trans()


  #### Current Team
  curr_team_indices = []
  for player_name in CURRENT_TEAM:
    player_arr = getPlayer(players, player_name)
    if len(player_arr) > 1:
      print "Too many people with name {0}".format(player_name)
      Tracer()()
    else:
      curr_team_indices.append(players.index(player_arr[0]))
  curr_team = [0]*numplayers
  for x in curr_team_indices:
    curr_team[x] = 1
  ####
  Tracer()()

  save_filename = 'player-optimization-data.mat'
  print "Saving variables as {0}".format('player-optimization-data.mat')
  sio.savemat(save_filename, {'A':A,'B':B,'G':G,'H':H,'Q':Q,'Q_new':Q_new,'days':days, 'curr_team':curr_team, 'numplayers':numplayers,'substitutions':SUBSTITUTIONS,'scores':Q,'start_index':start_index})

def find_naive_one_time_best_team(Q,A,B,G,H):
  # Tracer()()
  Q = matrix(Q)
  best_team = conelp(Q,G,H,A=A,b=B)
  team = [int(round(s)) for s in best_team['x']]
  players_np = np.array(players)
  scores_np = np.array(scores)
  team_players = players_np[np.nonzero(team)].tolist()
  team_player_scores = scores_np[np.nonzero(team)].tolist()
  print team_player_scores
  print team_players

def scoreAlgo3WithStat(player, stats, is_international = False):
  battingpoints = 0
  bowlingpoints = 0
  fieldingpoints = 0
  battingstats = stats['battingStats']
  bowlingstats = stats['bowlingStats']
  fieldingstats = stats['fieldingStats']
  if is_international:
    battingstats = battingstats[0]
    bowlingstats = bowlingstats[0]
    fieldingstats = fieldingstats[0]
    # avgrun = np.mean([x['r'] for x in player.tournamentStats['international']['battingStats'][1]])
    # stdrun = np.std([x['r'] for x in player.tournamentStats['international']['battingStats'][1]])
    # if battingstats['i'] >= 10:
    #   print "{0} {1:.2f}, {2:.2f} \t {3:.2f}".format(player.name, avgrun, stdrun, avgrun-stdrun)
  # Batting


  innings = float(battingstats['i'])
  matches = float(battingstats['m'])
  if not innings == 0:
    expected_runs = int(battingstats['r'])/innings
    try:
      strike_rate = float(battingstats['sr'])
    except:
      strike_rate = 0
    sixes = int(battingstats['6s'])
    battingpoints = expected_runs + expected_runs*(strike_rate/100) + 10*math.floor(expected_runs/25) + 2*(sixes/innings)
    battingpoints = battingpoints

  #Bowling

  innings = float(bowlingstats['i'])
  matches = float(bowlingstats['m'])
  if not innings == 0:
    wickets = int(bowlingstats['w'])
    balls = int(bowlingstats['b'])
    maidens = int(bowlingstats['maid'])
    runs_given = int(bowlingstats['r'])
    dots = (1.2*balls - runs_given)
    econscore = (1.5*balls - runs_given)/innings
    if econscore > 0:
      econscore *= 2
    bowlingpoints = econscore + 20*(wickets/innings) + 10*math.floor((wickets/innings)/2) + 20*(maidens/innings) + (dots/innings)
    bowlingpoints = bowlingpoints

  # if "McCull" in player.name:
  #   Tracer()()
  #Fielding


  matches = float(fieldingstats['m'])
  catches = int(fieldingstats['c'])
  stumpings = int(fieldingstats['s'])
  fieldingpoints = 10*(catches/matches) + 15*(stumpings/matches)

  if matches < 10:
    battingpoints/=(10-matches)
    bowlingpoints/=(10-matches)
    fieldingpoints/=(10-matches)
  totalpoints = battingpoints + bowlingpoints + fieldingpoints
  print "{0}\t\tBat: {1}\tBowl: {2}\tField: {3}\tTotal:{4}".format(player, battingpoints, bowlingpoints, fieldingpoints, totalpoints)

  # if "Doeschate" in player.name:
  #   Tracer()()

  return [totalpoints, battingpoints, bowlingpoints, fieldingpoints]


# Simple scoring based on Fantasy league rules and dumb past estimates
def scorePlayerAlgo3(player):
  # if "Vinay" in player.name:
  #   Tracer()()
  if not hasattr(player, "tournamentStats"):
    return -1,-1,-1,-1
  if player.tournamentStats["all"] == -1:
    print player
    return -1,-1,-1,-1
  stats = player.tournamentStats["all"]
  noninternational = True
  intstats = [0,0,0,0]
  if "battingStats" in player.tournamentStats["international"]:
    noninternational = False
    # Tracer()()
    intstats = scoreAlgo3WithStat(player, player.tournamentStats["international"],True)
  otherstats = scoreAlgo3WithStat(player, player.tournamentStats["all"])
  finalstats = [0.5*x + 0.5*y for x,y in zip(otherstats,intstats)]


  # print "{0}\t\tBat: {1}\tBowl: {2}\tField: {3}\tTotal:{4}".format(player, finalstats[1], finalstats[2], finalstats[3], finalstats[0])

  return tuple(finalstats)



# Simple scoring based on Fantasy league rules and dumb past estimates
def scorePlayerAlgo1(player):
  if not hasattr(player, "tournamentStats"):
    return -1,-1,-1,-1
  ipl13stats = [x for x in player.tournamentStats if x[0] == 'ipl2013']
  if len(ipl13stats) == 0:
    # Tracer()()
    return -1,-1,-1,-1
  stats = ipl13stats[0][1]
  battingpoints = 0
  bowlingpoints = 0
  fieldingpoints = 0



  # Batting
  battingstats = stats['battingStats']
  innings = float(battingstats['inns'])
  matches = float(battingstats['m'])
  if not innings == 0:
    expected_runs = int(battingstats['r'])/innings
    try:
      strike_rate = float(battingstats['sr'])
    except:
      strike_rate = 0
    sixes = int(battingstats['6s'])
    battingpoints = expected_runs + expected_runs*(strike_rate/100) + 10*math.floor(expected_runs/25) + 2*(sixes/innings)
    battingpoints = (innings/16.0)*battingpoints

  #Bowling
  bowlingstats = stats['bowlingStats']
  innings = float(bowlingstats['inns'])
  matches = float(bowlingstats['m'])
  if not innings == 0:
    wickets = int(bowlingstats['w'])
    balls = int(bowlingstats['b'])
    maidens = int(bowlingstats['maid'])
    dots = int(bowlingstats['d'])
    runs_given = int(bowlingstats['r'])
    econscore = (1.5*balls - runs_given)/innings
    if econscore > 0:
      econscore *= 2
    bowlingpoints = econscore + 20*(wickets/innings) + 10*math.floor((wickets/innings)/2) + 20*(maidens/innings) + (dots/innings)
    bowlingpoints = (innings/16.0)*bowlingpoints

  #Fielding
  fieldingstats = stats['fieldingStats']
  matches = float(fieldingstats['m'])
  catches = int(fieldingstats['c'])
  stumpings = int(fieldingstats['s'])
  runouts = int(fieldingstats['ro'])
  fieldingpoints = 10*(catches/matches) + 15*(stumpings/matches) + 12.5*(runouts/matches)

  # if "Matt" in player.name:
  #   Tracer()()

  totalpoints = battingpoints + bowlingpoints + fieldingpoints
  print "{0}\t\tBat: {1}\tBowl: {2}\tField: {3}\tTotal:{4}".format(player, battingpoints, bowlingpoints, fieldingpoints, totalpoints)

  return totalpoints, battingpoints, bowlingpoints, fieldingpoints


 # Simple scoring based on Fantasy league rules and dumb past estimates
def scorePlayerAlgo2(player):
  if not hasattr(player, "tournamentStats"):
    return -1,-1,-1,-1
  if len(player.tournamentStats) == 0:
    # Tracer()()
    return -1,-1,-1,-1
  allfieldingstats = [t[1]['fieldingStats'] for t in player.tournamentStats]
  compiled_fielding_stats = {}
  for afs in allfieldingstats[0].viewkeys():
    compiled_fielding_stats[afs] = []
  for fs in allfieldingstats:
    for afs in fs.viewkeys():
      compiled_fielding_stats[afs].append(float(fs[afs]))

  allbowlingstats = [t[1]['bowlingStats'] for t in player.tournamentStats]
  compiled_bowling_stats = {}

  for afs in allbowlingstats[0].viewkeys():
    compiled_bowling_stats[afs] = []
  for fs in allbowlingstats:
    for afs in fs.viewkeys():
      try:
        if not fs[afs] == '-':
          compiled_bowling_stats[afs].append(float(fs[afs]))
        else:
          compiled_bowling_stats[afs].append(0.0)
      except:
        Tracer()()

  allbattingstats = [t[1]['battingStats'] for t in player.tournamentStats]
  compiled_batting_stats = {'a':[], 'b':[], 'inns':[], 'no':[], 'sr':[], 'm':[], '4s':[], '6s':[], 'hs':[], 'r':[], '100s':[], '50s':[]}
  for afs in allbattingstats[0].viewkeys():
    compiled_batting_stats[afs] = []
  for fs in allbattingstats:
    for afs in fs.viewkeys():
      try:
        if not afs in compiled_batting_stats:
          compiled_batting_stats[afs].append(0.0)
        if type(fs[afs]) is int:
          compiled_batting_stats[afs].append(float(fs[afs]))
        elif fs[afs][-1] == '*':
          compiled_batting_stats[afs].append(float(fs[afs][:-1]))
        elif not fs[afs] == '-':
          compiled_batting_stats[afs].append(float(fs[afs]))
      except Exception as e:
        Tracer()()

  stats = {}
  stats['bowlingStats'] = {}
  stats['bowlingStats']['r'] = sum(compiled_bowling_stats['r'])
  stats['bowlingStats']['inns'] = sum(compiled_bowling_stats['inns'])
  stats['bowlingStats']['10w'] = sum(compiled_bowling_stats['10w'])
  stats['bowlingStats']['nb'] = sum(compiled_bowling_stats['nb'])
  stats['bowlingStats']['wb'] = sum(compiled_bowling_stats['wb'])
  stats['bowlingStats']['maid'] = sum(compiled_bowling_stats['maid'])
  stats['bowlingStats']['4w'] = sum(compiled_bowling_stats['4w'])
  stats['bowlingStats']['5w'] = sum(compiled_bowling_stats['5w'])
  stats['bowlingStats']['b'] = sum(compiled_bowling_stats['b'])
  stats['bowlingStats']['wmaid'] = sum(compiled_bowling_stats['wmaid'])
  stats['bowlingStats']['m'] = sum(compiled_bowling_stats['m'])
  stats['bowlingStats']['6s'] = sum(compiled_bowling_stats['6s'])
  stats['bowlingStats']['4s'] = sum(compiled_bowling_stats['4s'])
  stats['bowlingStats']['ov'] = sum(compiled_bowling_stats['ov'])
  stats['bowlingStats']['w'] = sum(compiled_bowling_stats['w'])
  stats['bowlingStats']['d'] = sum(compiled_bowling_stats['d'])
  stats['bowlingStats']['e'] = 6*stats['bowlingStats']['r']/stats['bowlingStats']['b'] if stats['bowlingStats']['b']!=0 else sys.float_info.max
  stats['bowlingStats']['sr'] = 100*stats['bowlingStats']['w']/stats['bowlingStats']['b'] if stats['bowlingStats']['b']!=0 else sys.float_info.max
  stats['bowlingStats']['a'] = stats['bowlingStats']['r']/stats['bowlingStats']['w'] if stats['bowlingStats']['w']!=0 else sys.float_info.max
  stats['bowlingStats']['bbmw'] = max(compiled_bowling_stats['bbmw'])
  stats['bowlingStats']['bbiw'] = max(compiled_bowling_stats['bbiw'])
  tmpind = compiled_bowling_stats['bbmr'].index(min([compiled_bowling_stats['bbmr'][j] for j in [i for i,val in enumerate(compiled_bowling_stats['bbmw']) if val==stats['bowlingStats']['bbmw']] ]))
  stats['bowlingStats']['bbmr'] = compiled_bowling_stats['bbmr'][tmpind]
  tmpind = compiled_bowling_stats['bbir'].index(min([compiled_bowling_stats['bbir'][j] for j in [i for i,val in enumerate(compiled_bowling_stats['bbiw']) if val==stats['bowlingStats']['bbiw']] ]))
  stats['bowlingStats']['bbir'] = compiled_bowling_stats['bbir'][tmpind]


  stats['battingStats'] = {}
  stats['battingStats']['r'] = sum(compiled_batting_stats['r'])
  stats['battingStats']['inns'] = sum(compiled_batting_stats['inns'])
  stats['battingStats']['no'] = sum(compiled_batting_stats['no'])
  stats['battingStats']['b'] = sum(compiled_batting_stats['b'])
  stats['battingStats']['m'] = sum(compiled_batting_stats['m'])
  stats['battingStats']['100s'] = sum(compiled_batting_stats['100s'])
  stats['battingStats']['50s'] = sum(compiled_batting_stats['50s'])
  stats['battingStats']['4s'] = sum(compiled_batting_stats['4s'])
  stats['battingStats']['6s'] = sum(compiled_batting_stats['6s'])
  stats['battingStats']['hs'] = max(compiled_batting_stats['hs'])
  stats['battingStats']['a'] = stats['battingStats']['r']/(stats['battingStats']['inns']-stats['battingStats']['no']) if (stats['battingStats']['inns']-stats['battingStats']['no'])!=0 else sys.float_info.max
  stats['battingStats']['sr'] = 100*stats['battingStats']['r']/ stats['battingStats']['b'] if stats['battingStats']['b'] else sys.float_info.max
  stats['fieldingStats'] = {}
  stats['fieldingStats']['m'] = sum(compiled_fielding_stats['m'])
  stats['fieldingStats']['inns'] = sum(compiled_fielding_stats['inns'])
  stats['fieldingStats']['c'] = sum(compiled_fielding_stats['c'])
  stats['fieldingStats']['ro'] = sum(compiled_fielding_stats['ro'])
  stats['fieldingStats']['s'] = sum(compiled_fielding_stats['s'])

  # Tracer()()
  battingpoints = 0
  bowlingpoints = 0
  fieldingpoints = 0



  # Batting
  battingstats = stats['battingStats']
  innings = float(battingstats['inns'])
  matches = float(battingstats['m'])
  if not innings == 0:
    expected_runs = int(battingstats['r'])/innings
    try:
      strike_rate = float(battingstats['sr'])
    except:
      strike_rate = 0
    sixes = int(battingstats['6s'])
    battingpoints = expected_runs + expected_runs*(strike_rate/100) + 10*math.floor(expected_runs/25) + 2*(sixes/innings)
    battingpoints = battingpoints

  #Bowling
  bowlingstats = stats['bowlingStats']
  innings = float(bowlingstats['inns'])
  matches = float(bowlingstats['m'])
  if not innings == 0:
    wickets = int(bowlingstats['w'])
    balls = int(bowlingstats['b'])
    maidens = int(bowlingstats['maid'])
    dots = int(bowlingstats['d'])
    runs_given = int(bowlingstats['r'])
    econscore = (1.5*balls - runs_given)/innings
    if econscore > 0:
      econscore *= 2
    bowlingpoints = econscore + 20*(wickets/innings) + 10*math.floor((wickets/innings)/2) + 20*(maidens/innings) + (dots/innings)
    bowlingpoints = bowlingpoints

  #Fielding
  fieldingstats = stats['fieldingStats']
  matches = float(fieldingstats['m'])
  catches = int(fieldingstats['c'])
  stumpings = int(fieldingstats['s'])
  runouts = int(fieldingstats['ro'])
  fieldingpoints = 10*(catches/matches) + 15*(stumpings/matches) + 12.5*(runouts/matches)

  # if "South" in player.name:
  #   Tracer()()

  if matches < 5:
    battingpoints/=(5-matches)
    bowlingpoints/=(5-matches)
    fieldingpoints/=(5-matches)


  totalpoints = battingpoints + bowlingpoints + fieldingpoints
  print "{0}\t\tBat: {1}\tBowl: {2}\tField: {3}\tTotal:{4}".format(player, battingpoints, bowlingpoints, fieldingpoints, totalpoints)

  return totalpoints, battingpoints, bowlingpoints, fieldingpoints

def pickTeam(players, schedule):
  scores = []
  bat_scores = []
  bowl_scores = []
  field_scores = []
  # Get all tournament names
  # set([z.encode('ascii','ignore') for y in [[x[0] for x in p.tournamentStats] for p in players if hasattr(p,'tournamentStats')] for z in y])
  for player in players:
    score, bat_score, bowl_score, field_score = scorePlayerAlgo3(player)
    scores.append(score)
    bat_scores.append(bat_score)
    bowl_scores.append(bowl_score)
    field_scores.append(field_score)
  # Sorted scores
  sortedscores = sorted(zip(players,scores,bat_scores, bowl_scores, field_scores), key=lambda x: x[1])
  Tracer()()
  setUpAndSaveVars(players, scores, schedule)

def main():
  if len(sys.argv) <= 2:
    print "Run as pickTeam.py <data pickle file name> <schedule pickle file name>"
    sys.exit()
  file_to_parse = sys.argv[1]
  file2_to_parse = sys.argv[2]
  if not os.path.isfile(file_to_parse):
    print "{0} does not exist.".format(file_to_parse)
    sys.exit()
  if not os.path.isfile(file2_to_parse):
    print "{0} does not exist.".format(file2_to_parse)
    sys.exit()
  f = open(file_to_parse)
  global data
  data = pickle.load(f)
  f.close()
  g = open(file2_to_parse)
  schedule = pickle.load(g)
  g.close()
  pickTeam(data, schedule)
  # Tracer()()


if __name__ == '__main__':
  main()
