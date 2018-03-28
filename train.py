
class Train(object):

    # trainNum
    # daysOfWeek
    # criticalLevel
    def __init__(self, params): # params is a list of strings
        super([object Object], self).__init__()

        self.trainNumber = params[0]
        self.trainStartingStation = params[1]

        self.daysOfWeek = params[2]
        if self.daysOfWeek == 'once' or self.daysOfWeek == '0':
            self.justOnce = True
        else: daysOfWeek = list(map(int, list(daysOfWeek)))

        self.criticalLevel = params[3] in ['true', 'iscritical', 'critical']
        # TODO not a single value but from 0 to 3
        # self.state = params[4] # paused or not
