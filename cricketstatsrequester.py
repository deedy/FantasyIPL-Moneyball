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


class CricketStatsRequester:
    def __init__(self, player):
        self.name = player.name
        self.player = Player(player)

    def getStats(self):
        url_name = self.name.replace(" ","%20")
        playerIDurl =  "http://search.espncricinfo.com/ci/content/site/search.html?search={0}&gblsearch=".format(url_name)
        data = self.requestWebsite(playerIDurl)
        only_result =  SoupStrainer('div',{'id': 'plysRslt'})
        soup = BeautifulSoup(data,"html.parser", parse_only=only_result)
        match = re.search("/ci/content/player/(\d{1,})",str(soup))
        if not match:
            print "Couldn't find player with name {0}".format(self.name)
        playerID = match.groups()[0]
        self.playerID = playerID
        self.player.setESPNid(self.playerID)
        print "{0} ESPNCricInfo ID found: {1}".format(self.name,self.playerID)

        print "Fetching {0}'s Twenty20 Cumulative Stats...".format(self.name)
        all2020 = self.getTwenty20Data(self.playerID)
        if all2020 == -1:
            print "No T20 Data available for this player"
            var = raw_input("Please manually enter ESPNCricInfo ID: ")
            self.playerID = var
            self.player.setESPNid(self.playerID)
            all2020 = self.getTwenty20Data(self.playerID)


        # Tracer()()
        all_data = {}
        print "Fetching {0}'s Bowling Stats...".format(self.name)
        all_data['bowlingStats'] = self.getBowlingData(playerID)
        if all_data['bowlingStats'] == (-1, -1):
            print "No International T20 Data available for this player"
        else:
            print "Fetching {0}'s Batting Stats...".format(self.name)
            all_data['battingStats'] = self.getBattingData(playerID)
            print "Fetching {0}'s Fieldings Stats...".format(self.name)
            all_data['fieldingStats'] = self.getFieldingData(playerID)
        # Tracer()()

        final_data ={}
        final_data['international'] = all_data
        final_data['all'] = all2020
        self.player.setDetailedStats(final_data)
        pickle.dump(self.player, open("Data-Rich/player-"+self.name.replace(" ","-"), "wb" ) )
        print "{0}'s data file saved\n\n".format(self.name)
        return self.player

    def getTwenty20Data(self, playerID):
        statsURL = "http://www.espncricinfo.com/ci/content/player/{0}.html".format(self.playerID)
        rawstats = self.requestWebsite(statsURL)
        soup = BeautifulSoup(rawstats)
        res = soup('b', text="Twenty20")
        if len(res) == 0:
            return -1
        batting = self.parseSingleDataStr(str(res[0].parent.parent))
        bowling = self.parseSingleDataStr(str(res[1].parent.parent))
        batting.insert(-4,-1)
        del bowling[7]
        bowling.insert(4,0)
        fielding = ['overall', batting[1], batting[1], int(batting[-1])+int(batting[-2]), batting[-2], batting[-1], 0.0, batting[-2]]
        batting_stats = self.parseOverallBattingData(batting[:-2])
        bowling_stats = self.parseOverallBowlingData(bowling[:-1])
        fielding_stats = self.parseOverallFieldingData(fielding)
        all2020 = {}
        all2020['battingStats'] = batting_stats
        all2020['bowlingStats'] = bowling_stats
        all2020['fieldingStats'] = fielding_stats
        return all2020


    def getFieldingData(self, playerID):
        statsURL = "http://stats.espncricinfo.com/ci/engine/player/{0}.html?class=3;orderby=start;orderbyad=reverse;template=results;type=fielding;view=innings".format(self.playerID)
        rawstats = self.requestWebsite(statsURL)
        only_data = SoupStrainer(class_="data1")
        soup2 = BeautifulSoup(rawstats,"html.parser", parse_only=only_data)

        total = self.parseSingleDataStr(str(soup2.contents[0]))
        innings_data = [self.parseSingleDataStr(str(i)) for i in soup2.contents[1:]]
        if total[0]=="No records available to match this query":
            return (-1,-1)
        innings_data = self.parseInningsFieldingData(innings_data)
        overall_data = self.parseOverallFieldingData(total)
        return (overall_data, innings_data)


    def parseOverallFieldingData(self, overall_data):
        overall_stats = {}
        if len(overall_data[1]) == 9:
            overall_stats['span_s'] = float(overall_data[1][:4])
            overall_stats['span_f'] = float(overall_data[1][-4:])
        else:
            overall_data.insert(1,0)
        overall_stats['m'] = float(overall_data[2])
        overall_stats['i'] = float(overall_data[3])
        overall_stats['dismissals'] = float(overall_data[4])
        overall_stats['c'] = float(overall_data[5])
        overall_stats['s'] = float(overall_data[6])
        overall_stats['ctw'] = float(overall_data[7])
        overall_stats['ctf'] = float(overall_data[8])
        return overall_stats


    def parseInningsFieldingData(self, innings_data):
        res = []
        for inn in innings_data:
            innings = {}
            if inn[0].strip() == 'DNF' or inn[0].strip() == 'TDNF' :
                continue
            innings['dismissals'] = float(inn[0])
            innings['c'] = float(inn[1])
            innings['s'] = float(inn[2])
            innings['ctw'] = float(inn[3])
            innings['ctf'] = float(inn[4])
            innings['inning'] = int(inn[5])
            innings['opp'] = inn[7]
            innings['place'] = inn[8]
            innings['date'] = time.strptime(inn[9],"%d %b %Y")
            innings['t20i_num'] = int(re.search(" (\d+$)",inn[10]).groups()[0])
            res.append(innings)
        return res

    def getBowlingData(self, playerID):
        statsURL = "http://stats.espncricinfo.com/ci/engine/player/{0}.html?class=3;orderby=start;orderbyad=reverse;template=results;type=bowling;view=innings".format(self.playerID)
        rawstats = self.requestWebsite(statsURL)
        only_data = SoupStrainer(class_="data1")
        soup2 = BeautifulSoup(rawstats,"html.parser", parse_only=only_data)

        total = self.parseSingleDataStr(str(soup2.contents[0]))
        innings_data = [self.parseSingleDataStr(str(i)) for i in soup2.contents[1:]]
        if total[0]=="No records available to match this query":
            return (-1,-1)
        innings_data = self.parseInningsBowlingData(innings_data)
        overall_data = self.parseOverallBowlingData(total)
        return (overall_data, innings_data)


    def parseOverallBowlingData(self, overall_data):
        overall_stats = {}
        if len(overall_data[1]) == 9:
            overall_stats['span_s'] = float(overall_data[1][:4])
            overall_stats['span_f'] = float(overall_data[1][-4:])
        else:
            overall_data.insert(1,0)
        overall_stats['m'] = float(overall_data[2])
        if not overall_data[3] == '-':
            overall_stats['i'] = float(overall_data[3])
        else:
            overall_stats['i'] = 0.0
        if not overall_data[4] == '-':
            if '.' in overall_data[4]:
                overall_stats['b'] = float(overall_data[4][-1])+float(overall_data[4][:-2])*6
            else:
                overall_stats['b'] = float(overall_data[4])
        else:
            overall_stats['b'] = 0.0
        overall_stats['maid'] = float(overall_data[5]) if not overall_data[5] == '-' else 0.0
        overall_stats['r'] = float(overall_data[6]) if not overall_data[6] == '-' else 0.0
        overall_stats['w'] = float(overall_data[7]) if not overall_data[7] == '-' else 0.0
        if not overall_data[8] == '-':
            overall_stats['bbiw'] = float(overall_data[8][0])
            overall_stats['bbir'] = float(overall_data[8][2:])
        else:
            overall_stats['bbiw'] = -1.0
            overall_stats['bbir'] = -1.0
        if not overall_stats['w'] == 0.0:
            overall_stats['a'] = overall_stats['r']/overall_stats['w']
        else:
            overall_stats['a'] = -1.0
        if not overall_stats['b'] == 0.0:
            overall_stats['e'] = 6*overall_stats['r']/overall_stats['b']
        else:
            overall_stats['e'] = -1.0
        if not overall_stats['w'] == 0.0:
            overall_stats['sr'] = overall_stats['b']/overall_stats['w']
        else:
            overall_stats['sr'] = -1.0
        overall_stats['4w'] = float(overall_data[12]) if not overall_data[13] == '-' else 0.0
        overall_stats['5w'] = float(overall_data[13]) if not overall_data[13] == '-' else 0.0
        return overall_stats


    def parseInningsBowlingData(self, innings_data):
        res = []
        for inn in innings_data:
            innings = {}
            if inn[0].strip() == 'DNB' or inn[0].strip() == 'TDNB' :
                continue
            innings['b'] = float(inn[0][-1])+float(inn[0][:-2])*6
            innings['maid'] = float(inn[1])
            innings['r'] = float(inn[2])
            innings['w'] = float(inn[3])
            innings['e'] = 6*innings['r']/innings['b']
            innings['pos'] = int(inn[5])
            innings['inning'] = int(inn[6])
            innings['opp'] = inn[8]
            innings['place'] = inn[9]
            innings['date'] = time.strptime(inn[10],"%d %b %Y")
            innings['t20i_num'] = int(re.search(" (\d+$)",inn[11]).groups()[0])
            res.append(innings)
        return res


    def getBattingData(self, playerID):
        statsURL = "http://stats.espncricinfo.com/ci/engine/player/{0}.html?class=3;orderby=start;orderbyad=reverse;template=results;type=batting;view=innings".format(self.playerID)
        rawstats = self.requestWebsite(statsURL)
        only_data = SoupStrainer(class_="data1")
        soup2 = BeautifulSoup(rawstats,"html.parser", parse_only=only_data)

        total = self.parseSingleDataStr(str(soup2.contents[0]))
        innings_data = [self.parseSingleDataStr(str(i)) for i in soup2.contents[1:]]
        if total[0]=="No records available to match this query":
            return (-1,-1)
        innings_data = self.parseInningsBattingData(innings_data)
        overall_data = self.parseOverallBattingData(total)
        return (overall_data, innings_data)


    def parseOverallBattingData(self, overall_data):
        overall_stats = {}
        if len(overall_data[1]) == 9:
            overall_stats['span_s'] = float(overall_data[1][:4])
            overall_stats['span_f'] = float(overall_data[1][-4:])
        else:
            overall_data.insert(1,0)
        overall_stats['m'] = float(overall_data[2])
        overall_stats['i'] = float(overall_data[3]) if not overall_data[3] == '-' else 0.0
        overall_stats['no'] = float(overall_data[4])  if not overall_data[4] == '-' else 0.0
        overall_stats['r'] = float(overall_data[5]) if not overall_data[5] == '-' else 0.0
        if overall_data[6][-1]=='*':
            overall_data[6] = overall_data[6][:-1]
        overall_stats['hs'] = float(overall_data[6]) if not overall_data[6] == '-' else 0.0
        if not (overall_stats['i']-overall_stats['no']) == 0:
            overall_stats['a'] = overall_stats['r']/(overall_stats['i']-overall_stats['no'])
        else:
            overall_stats['a'] = -1.0
        overall_stats['b'] = float(overall_data[8]) if not overall_data[8] == '-' else 0.0
        overall_stats['sr'] = 100*overall_stats['r']/overall_stats['b'] if not overall_stats['b'] == 0.0 else 0.0
        overall_stats['100s'] = float(overall_data[10]) if not overall_data[10] == '-' else 0.0
        overall_stats['50s'] = float(overall_data[11]) if not overall_data[11] == '-' else 0.0
        overall_stats['0s'] = float(overall_data[12]) if not overall_data[12] == '-' else 0.0
        overall_stats['4s'] = float(overall_data[13]) if not overall_data[13] == '-' else 0.0
        overall_stats['6s'] = float(overall_data[14]) if not overall_data[14] == '-' else 0.0
        return overall_stats


    def parseInningsBattingData(self, innings_data):
        res = []
        for inn in innings_data:
            innings = {}
            if inn[0].strip() == 'DNB' or inn[0].strip() == 'TDNB' or inn[0].strip() == 'absent' :
                continue
            if inn[0][-1] == '*':
                innings['no'] = True
                innings['r'] = float(inn[0][:-1])
            else:
                innings['r'] = float(inn[0])
            if not inn[1] == '-':
                innings['minutes'] = float(inn[1])
            else:
                innings['minutes'] = -1.0
            innings['b'] = float(inn[2])
            innings['4s'] = float(inn[3])
            innings['6s'] = float(inn[4])
            if not innings['b'] == 0.0:
                innings['sr'] = 100*innings['r']/innings['b']
            else:
                innings['sr'] = 0.0
            innings['pos'] = int(inn[6])
            innings['dismiss'] = inn[7]
            innings['inning'] = int(inn[8])
            innings['opp'] = inn[10]
            innings['place'] = inn[11]
            innings['date'] = time.strptime(inn[12],"%d %b %Y")
            innings['t20i_num'] = int(re.search(" (\d+$)",inn[13]).groups()[0])
            res.append(innings)
        return res


    def parseSingleDataStr(self, datastr):
        soup_data = BeautifulSoup(datastr.replace("\n",""))
        rawelements = soup_data.findAll(text=True)
        elements = [str(a) for a in rawelements]
        return elements


    def requestWebsite(self, url):
        req = Request(url)
        try:
            response = urlopen(req)
        except URLError as e:
            if hasattr(e, 'reason'):
                print 'We failed to reach a server.'
                print 'Reason: ', e.reason
            elif hasattr(e, 'code'):
                print 'The server couldn\'t fulfill the request.'
                print 'Error code: ', e.code
        data = response.read()
        response.close()
        return data



def main():
  if len(sys.argv) <= 1:
    print "Run as cricketstatsrequester.py <data pickle file name>"
    sys.exit()
  file_to_parse = sys.argv[1]
  if not os.path.isfile(file_to_parse):
    print "{0} does not exist.".format(file_to_parse)
    sys.exit()
  f = open(file_to_parse)
  data = pickle.load(f)
  new_player_list = []
  for player in data:
      csr = CricketStatsRequester(player)
      if player.name == "Francois du Plessis":
        name_to_use = "Faf du Plessis"
      elif player.name == "Jaidev Unadkat":
        name_to_use = "Jaydev Unadkat"
      else:
        name_to_use = player.name


      file_to_write = "Data-Rich/player-"+name_to_use.replace(" ","-")

      if not os.path.isfile(file_to_write):
        new_player_list.append(csr.getStats())
      else:
        g = open(file_to_write)
        datasaved = pickle.load(g)
        new_player_list.append(datasaved)
  print "complete dump"
  pickle.dump(new_player_list, open("IPL-Complete-Stats-2.pik", "wb" ))
  f.close()

if __name__ == '__main__':
  main()

