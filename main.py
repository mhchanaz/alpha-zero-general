import logging
import coloredlogs

from Coach import Coach
from connect4.Connect4Game import Connect4Game as Game
from connect4.keras.NNet import NNetWrapper as nn
from utils import *

import ray
ray.init()

log = logging.getLogger(__name__)

coloredlogs.install(level='INFO')  # Change this to DEBUG to see more info.

raw_args = {
    'numIters': 1000,
    'numEps': 100,              # Number of complete self-play games to simulate during a new iteration.
    'tempThreshold': 15,        #
    'updateThreshold': 0,     # During arena playoff, new neural net will be accepted if threshold or more of games are won.
    'maxlenOfQueue': 200000,    # Number of game examples to train the neural networks.
    'numMCTSSims': 400,          # Number of games moves for MCTS to simulate.
    'arenaCompare': 0,         # Number of games to play during arena play to determine if new net will be accepted.
    'cpuct': 1,

    'checkpoint': './temp/',
    'load_model': False,
    'load_folder_file': ('./temp','best.h5'),
    'numItersForTrainExamplesHistory': 4,

}

args_ref = ray.put(raw_args)

def main():

    args = dotdict(raw_args)

    log.info('Loading %s...', Game.__name__)
    g = Game()

    log.info('Loading %s...', nn.__name__)
    nnet = nn(g)

    if args.load_model:
        log.info('Loading checkpoint "%s/%s...', args.load_folder_file[0], args.load_folder_file[1])
        nnet.load_checkpoint(g, args.load_folder_file[0], args.load_folder_file[1])
    else:
        log.warning('Not loading a checkpoint!')

    log.info('Loading the Coach...')
    c = Coach(g, nnet, args_ref)

    if args.load_model:
        log.info("Loading 'trainExamples' from file...")
        c.loadTrainExamples()

    log.info('Starting the learning process 🎉')
    c.learn()


if __name__ == "__main__":
    main()
