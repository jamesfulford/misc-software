# Potholes in Chicago.py
#
# An example of parsing potholes data and tabulating results.
# This program reads the CSV data and tabulates potholes
# according to zip-code.    Use this as a rough code template
# for solving the problem of finding the worst street on
# which to bike.

import csv
import operator  # used when sorting

# Dictionary used to tabulate results
blocks = {}
# key is street
# blocks[key] is a list of lists.
#   sublist[0] is blockNumber
#   sublist[1] is number of potholes

stretchWidth = 10


def getHoles(listOfBlocks, blockNumber):
    """
    returns how many holes a particular block has, given a list of
    blocks on a street and which blocknumber it is.
    """
    for block in listOfBlocks:
        if block[0] == blockNumber:
            return block[1]
    return 0


def getMinBlock(listOfBlocks):
    """
    returns the lowest block number on a street.
    West and South count as negative.
    """
    small = 100000000  # really big!
    for block in listOfBlocks:
        small = min(small, block[0])
    return small


def getMaxBlock(listOfBlocks):
    """
    returns the highest block number on a street.
    West and South count as negative.
    """
    big = -1000000000  # really not big!
    for block in listOfBlocks:
        big = max(big, block[0])
    return big


def bestStretch(listOfBlocks):
    """
    returns a tuple that holds information on the best stretch of
    blocks on the provided street:
        [0] is how many holes are in this stretch
        [1] is where the best stretch begins (block number)
        [2] is where the best stretch ends (block number)
    """
    mostHoles = 0
    bestStartBlock = 0
    bestEndBlock = 0
    for i in range(getMinBlock(listOfBlocks), getMaxBlock(listOfBlocks)):
        potholes = 0
        for j in range(i, i + stretchWidth):
            potholes += getHoles(listOfBlocks, j)
        if potholes > mostHoles:
            mostHoles = potholes
            bestStartBlock = i
            bestEndBlock = i + stretchWidth
    return (mostHoles, bestStartBlock, bestEndBlock)
# 0 is block range
# 1 is number of potholes


def assignToBlock(address):
    """
    given an address, returns:
        [0] which street this address is on
        [1] which block it belongs to.
    """
    parts = address.split()
    blockNumber = parts[0][:-2]
    try:
        blockNumber = int(blockNumber)
    except:
        blockNumber = 0
        # because of problems with 0 blocks not being like 0xx
    if parts[1].upper() in "W" or parts[1].upper() in "S":
        blockNumber *= -1
    street = " ".join(parts[2:])

    return(street, blockNumber)
    # 0 is street
    # 1 is blockNumber


def incrementBlock(address, blockNumber):
    """
    goes into blocks dictionary, changes this address' number of potholes
    to one more.
    """
    if address not in blocks:
        blocks[address] = [[blockNumber, 1]]
    else:
        foundBlock = False
        for block in blocks[address]:
            if block[0] == blockNumber:
                    foundBlock = True
                    block[1] += 1
                    break
        if not foundBlock:
            blocks[address].append([blockNumber, 1])


def evalStreets(blocks):
    """
    given a dictionary of streets corresponding to lists of blocks,
    returns a dictionary of streets corresponding to the best stretch of
    blocks on that street.
    """
    streets = dict()
    for street in blocks.keys():
        streets[street] = bestStretch(blocks[street])
    return streets


f = open('../../data/potholes.csv', 'r')
lineNumber = 0
for row in csv.DictReader(f):
    lineNumber += 1
    status = row['STATUS']
    if status.lower() in "open":
        here = assignToBlock(row['STREET ADDRESS'])
        thisAddress = here[0]
        thisBlock = here[1]
        incrementBlock(thisAddress, thisBlock)

streets = evalStreets(blocks)
top5 = dict(sorted(streets.iteritems(), key=operator.itemgetter(1),
            reverse=True)[:10])
# Thanks to StackOverflow for the sorting help:
# http://stackoverflow.com/questions/7197315/5-maximum-values-in-a-python-dictionary


def printDict(diction):
    """
    prints the provided dictionary, one line per entry. Format: "key : value"
    """
    print("\n")
    for entry in diction.keys():
        print(entry + " : " + str(diction[entry]) + "\n")

printDict(top5)
