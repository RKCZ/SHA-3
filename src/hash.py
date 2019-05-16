#! /usr/bin/python
'''
Created on 10 May 2019

@author: kalivoda
'''
from sys import argv, exit
from getopt import getopt, GetoptError
from keccak import keccak


def main(argv):    
    helpmsg = 'digest.py -i <inputfile> -o <outputfile>'
    inputBytes = ''
    inputfile = ''
    readFromFile = False
    writeToFile = False
    outputfile = ''
    try:
        opts, args = getopt(argv, "hi:o:", ["input=", "output="])
    except GetoptError:
        print(helpmsg)
        exit(2);
    for opt, arg in opts:
        if opt == '-h':
            print(helpmsg)
            exit()
        elif opt in ("-i", "--input"):
            inputfile = arg
            print("reading from {}".format(inputfile))
            readFromFile = True
            
        elif opt in ("-o", "--output"):
            outputfile = arg
            print("printing output to {}".format(outputfile))
            writeToFile = True
    
    try:
        hashLength = int(args[0])
    except ValueError:
        exit("first argument must be a valid hash length")
    
    if readFromFile:    
        with open(inputfile, 'rb') as f:
            inputBytes = f.read()
    else:
        inputBytes = args[1].encode()
    try:
        digest = keccak.SHA3(inputBytes, hashLength)
    except ValueError as e:
        exit("hashing failed: {}".format(str(e)))
    if writeToFile:
        with open(outputfile, 'wb') as f:
            f.write(digest)
    else:
        print(digest.hex())
    
    
if __name__ == '__main__':
    main(argv[1:])
            
