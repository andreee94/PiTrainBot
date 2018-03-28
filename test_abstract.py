
from usercommand import UserCommandDocs
from torrentcommand import TorrentCommand


commands = [UserCommandDocs, TorrentCommand] #, TrainCommand]

for c in commands:
    if c.getCommandName() == 'torrent':
        print(c.help())
