import sys
import os
from bs4 import BeautifulSoup
from bs4 import SoupStrainer
from bs4.diagnose import diagnose
from IPython.core.debugger import Tracer
import urllib2
import json
import re
import cPickle as pickle
from player import Player


def parsePlayersFromRawString(data):
  only_players =  SoupStrainer(class_="playerlist")
  soup = BeautifulSoup(data,"html.parser", parse_only=only_players)
  players = soup.find_all("div",class_="playerlist")
  parsed_player_list = []
  # Tracer()()
  for player in players:
    p_name = player.attrs['a'].encode('ascii', 'ignore')
    p_id = player.attrs['value'].encode('ascii', 'ignore')
    p_price = player.attrs['p'].encode('ascii', 'ignore')
    p_team = player.find(class_="teamsorting").text.encode('ascii', 'ignore')
    p_isoverseas = bool(player.find(class_="overseasimg"))
    p_isuncapped = bool( player.find(class_="uncappedimg"))
    skills = [False]*5;
    for skill in player.attrs['d']:
      skills[int(skill)] = True
    p_iskeeper = skills[1]
    p_isallrounder = skills[2]
    p_isbowler = skills[3]
    p_isbatsman = skills[4]
    parsed_player = Player(p_name, p_id, p_team, p_price)
    parsed_player.setBitValues(p_isoverseas, p_isuncapped, p_iskeeper, p_isallrounder, p_isbowler, p_isbatsman)
    print parsed_player
    parsed_player_list.append(parsed_player)
  return parsed_player_list

def reformatTournamentData(player):
  newStats = []
  if hasattr(player, "tournamentStats"):
    for index in player.tournamentStats:
      tournamentName = player.tournamentStats[index]['name']
      stats = {}
      tuplestat = (tournamentName, stats)
      stats['fieldingStats'] = player.tournamentStats[index]['fieldingStats']
      stats['battingStats'] = player.tournamentStats[index]['battingStats']
      stats['bowlingStats'] = player.tournamentStats[index]['bowlingStats']
      match_obj = re.search("20\d{2}", tournamentName)
      if not match_obj:
        continue
      year = int(match_obj.group())
      stats['year'] = year
      newStats.append(tuplestat)
    newStats.sort(key = lambda x : -x[1]['year'])
    player.setDetailedStats(newStats)

def getPlayerStats(parsed_player_list):
  prepend_url ="http://dynamic.pulselive.com/dynamic/data/core/cricket/careerStats/{0}_careerStats.js"
  urls = [(player, prepend_url.format(player.id)) for player in parsed_player_list]

  for player, url in urls:
    print "Fetching data for player {0}".format(player.name)
    request = urllib2.Request(url)
    response = urllib2.urlopen(request, timeout=10)
    player_data = response.read()
    if not player_data:
      print "No response from {0}".format(url)
      sys.exit()
    match_obj = re.search("\([^\)]{1,}\)", player_data)
    if not match_obj:
      print "Could not find appropriate JSON in {0}".format(player_data)
      sys.exit()
    raw_json_string = match_obj.group()[1:-1]
    json_data = json.loads(raw_json_string)

    p_dob = json_data["player"]["dateOfBirth"].encode('ascii', 'ignore')
    p_nationality = json_data["player"]["nationality"].encode('ascii', 'ignore')
    player.setDOBandNat(p_dob, p_nationality)

    if not "stats" in json_data:
      print "{0} is a n00b and doesn't have stats".format(player.name)
      continue
    tournament_data = {}
    for i in xrange(len(json_data["stats"])):
      if not "breakdown" in json_data["stats"][i]:
        print "Strange: no breakdown in one stats for {0}".format(player.name)
        continue
      for j in xrange(len(json_data["stats"][i]["breakdown"])):
        tournamentId = json_data["stats"][i]["breakdown"][j]["tournamentId"]["id"]
        if tournamentId in tournament_data:
          print "Duplicate tournament ID {0}".format(tournamentId)
          continue
        tournament_name = json_data["stats"][i]["breakdown"][j]["tournamentId"]["name"]
        tournament = {}
        tournament["name"] = tournament_name
        tournament["battingStats"] = json_data["stats"][i]["breakdown"][j]["battingStats"]
        tournament["bowlingStats"] = json_data["stats"][i]["breakdown"][j]["bowlingStats"]
        tournament["fieldingStats"] = json_data["stats"][i]["breakdown"][j]["fieldingStats"]
        tournament_data[tournamentId] = tournament
    player.setDetailedStats(tournament_data)
    reformatTournamentData(player)
    pickle.dump(player, open("player-"+player.name.replace(" ","-"), "wb" ) )
  pickle.dump(parsed_player_list, open("IPL-Complete-Stats.pik", "wb" ) )

def main():
  if len(sys.argv) <= 1:
    print "Run as parsePlayers.py <htmlfile of players to parse>"
    sys.exit()
  file_to_parse = sys.argv[1]
  if not os.path.isfile(file_to_parse):
    print "{0} does not exist.".format(file_to_parse)
    sys.exit()
  f = open(file_to_parse)
  data = f.read()
  parsed_player_list = parsePlayersFromRawString(data)
  getPlayerStats(parsed_player_list)
  f.close()

if __name__ == '__main__':
  main()



