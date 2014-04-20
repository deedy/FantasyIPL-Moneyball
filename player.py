class Player:
  def __init__(self, player):
    self.name = player.name
    self.id = player.id
    self.team = player.team
    self.price = player.price
    self.is_overseas = player.is_overseas
    self.is_uncapped = player.is_uncapped
    self.is_keeper = player.is_keeper
    self.is_allrounder = player.is_allrounder
    self.is_bowler = player.is_bowler
    self.is_batsman = player.is_batsman
    self.dob = player.dob
    self.nationality = player.nationality
    # self.tournamentStats = player.tournamentStats

  # def __init__(self, name, id, team, price):
  #   self.name = name
  #   self.id = id
  #   self.team = team
  #   self.price = price

  def setBitValues(self, is_overseas, is_uncapped, is_keeper, is_allrounder, is_bowler, is_batsman):
    self.is_overseas = is_overseas
    self.is_uncapped = is_uncapped
    self.is_keeper = is_keeper
    self.is_allrounder = is_allrounder
    self.is_bowler = is_bowler
    self.is_batsman = is_batsman

  def setDOBandNat(self, dob, nat):
    self.dob = dob
    self.nationality = nat

  def setDetailedStats(self, tournamentStats):
    self.tournamentStats = tournamentStats

  def setESPNid(self, id):
    self.espnid = id

  def __str__(self):
    return "{3} - {0} ({1}) \t ${2}\n".format(self.name, self.team, self.price, self.id)

  def __repr__(self):
    return self.__str__()
