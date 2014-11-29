""" Python version of the Santa 2014 Kaggle competition evaluation metric. """
__author__ = 'Joyce Noah-Vanhoucke'
__date__ = 'November 24, 2014'

import os
import csv
import time
import math
import datetime

from hours import Hours
from toy import Toy
from elf import Elf


def read_toys(toy_file, num_toys):
    """ Reads the toy file and returns a dictionary of Toys.
    Toy file format: ToyId, Arrival_time, Duration
        ToyId: toy id
        Arrival_time: time toy arrives. Format is: YYYY MM DD HH MM (space-separated)
        Duration: duration in minutes to build toy
    :param toy_file: toys input file
    :param hrs: hours object
    :param num_toys: total number of toys to build
    :return: Dictionary of toys
    """
    toy_dict = {}
    with open(toy_file, 'rb') as f:
        fcsv = csv.reader(f)
        fcsv.next()  # header row
        for row in fcsv:
            new_toy = Toy(row[0], row[1], row[2])
            toy_dict[new_toy.id] = new_toy
    if len(toy_dict) != num_toys:
        print '\n ** Read a file with {0} toys, expected {1} toys. Exiting.'.format(len(toy_dict), num_toys)
        exit(-1)
    return toy_dict


def score_submission(sub_file, myToys, hrs, NUM_ELVES):
    """ Score the submission file, performing constraint checking. Returns the time (in minutes) when
    final present is complete.
    :param sub_file: submission file name. Headers: ToyId, ElfId, Start_Time, Duration
    :param myToys: toys dictionary
    :param hrs: hours object
    :return: time (in minutes) when final present is complete
    """

    myElves = {}
    complete_toys = []
    last_minute = 0
    row_count = 0
    with open(sub_file, 'rb') as f:
        fcsv = csv.reader(f)
        fcsv.next()  # header
        for row in fcsv:
            row_count += 1
            if row_count % 50000 == 0:
                print 'Starting toy: {0}'.format(row_count)

            current_toy = row[0] 
            current_elf = int(row[1])
            start_minute = hrs.convert_to_minute(row[2])
            duration = int(row[3])

            if not current_toy in myToys:
                print 'Toy {0} not in toy dictionary.'.format(current_toy)
                exit(-1)
            elif myToys[current_toy].completed_minute > 0:
                print 'Toy {0} was completed at minute {1}'.format(current_toy, myToys[current_toy].completed_minute)
                exit(-1)

            if not 1 <= current_elf <= NUM_ELVES:
                print '\n ** Assigned elf does not exist: Elf {0}'.format(current_elf)
                exit(-1)

            # Create elf if this is the first time this elf is assigned a toy
            if not current_elf in myElves.keys():
                myElves[current_elf] = Elf(current_elf)

            # Check work starting constraints:
            # 1. within correct window of toy's arrival
            # 2. when elf is next allowed to work
            if myToys[current_toy].outside_toy_start_period(start_minute):
                print '\n ** Requesting work on Toy {0} at minute {1}: Work can start at {2} minutes'. \
                    format(current_toy, start_minute, myToys[current_toy].arrival_minute)
                exit(-1)
            if start_minute < myElves[current_elf].next_available_time:
                print '\n ** Elf {2} needs his rest, he is not available now ({0}) but will be later at {1}'. \
                    format(start_minute, myElves[current_elf].next_available_time, current_elf)
                exit(-1)

            # Check toy is complete based on duration and elf productivity
            if not myToys[current_toy].is_complete(start_minute, duration, myElves[current_elf].rating):
                print '\n ** Toy {0} is not complete'.format(current_toy)
                exit(-1)
            else:
                complete_toys.append(int(current_toy))
                if myToys[current_toy].completed_minute > last_minute:
                    last_minute = myToys[current_toy].completed_minute

           # Since toy started on time and is complete, update elf productivity
            myElves[current_elf].update_elf(hrs, myToys[current_toy], start_minute, duration)

    if len(complete_toys) != len(myToys):
        print "\n ** Not all toys are complete. Exiting."
        exit(-1)
    if max(complete_toys) != NUM_TOYS:
        print "\n ** max ToyId != NUM_TOYS."
        print "\n   max(complete_toys) = {0} versus NUM_TOYS = {1}".format(max(complete_toys), NUM_TOYS)
        exit(-1)
    else:
        score = last_minute * math.log(1.0 + len(myElves))
        print '\nSuccess!'
        print '  Score = {0}'.format(score)


# ======================================================================= #
# === MAIN === #

if __name__ == '__main__':
    """ Evaluation script for Helping Santa's Helpers, the 2014 Kaggle Holiday Optimization Competition. """

    start = time.time()

    NUM_TOYS = 10000000
    NUM_ELVES = 900

    toy_file = os.path.join(os.getcwd(), 'toys_rev2.csv')
    myToys = read_toys(toy_file, NUM_TOYS)
    print ' -- All toys read. Starting to score submission. '

    sub_file = os.path.join(os.getcwd(), 'sampleSubmission_rev2.csv')
    hrs = Hours()
    score_submission(sub_file, myToys, hrs, NUM_ELVES)

    print 'total time = {0}'.format(time.time() - start)




