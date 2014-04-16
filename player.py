class Player:
  def __init__(self, name, id, team, price):
    self.name = name
    self.id = id
    self.team = team
    self.price = price

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

  def __str__(self):
    return "{3} - {0} ({1}) \t ${2}\n".format(self.name, self.team, self.price, self.id)

  def __repr__(self):
    return self.__str__()
