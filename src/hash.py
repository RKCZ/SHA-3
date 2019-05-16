#! /usr/bin/python
'''
Created on 10 May 2019

@author: kalivoda
'''
from sys import argv, exit, stdin
from getopt import getopt, GetoptError
from keccak import keccak
import codecs
import logging


def main(argv):    
    helpmsg = 'hash.py -i <inputfile> -o <outputfile>'
    inputfile = ''
    readFromFile = False
    writeToFile = False
    outputfile = ''
    inputText = ''
    hashLength = 224

    try:
        opts, args = getopt(argv, "hi:o:l:", ["input=", "output=", "length="])
    except GetoptError:
        print(helpmsg)
        exit(2);

    for opt, arg in opts:
        if opt == '-h':
            print(helpmsg)
            exit()
        elif opt in ("-i", "--input"):
            inputfile = arg
            readFromFile = True
            
        elif opt in ("-o", "--output"):
            outputfile = arg
            writeToFile = True
        elif opt in ("-l", "--length"):
            hashLength = arg

    if readFromFile:    
        with open(inputfile, 'rb') as f:
            inputText = f.read().decode()
    else:
        if len(args) < 1:
            inputText = stdin.read().decode()
        else:
            inputText = args[0]
            
    try:
        logging.debug("Input message = {}".format(inputText))
        digest = keccak.SHA3(inputText.encode(), hashLength)
    except ValueError as e:
        exit("hashing failed: {}".format(str(e)))
        
    if writeToFile:
        with open(outputfile, 'wb') as f:
            f.write(codecs.decode(codecs.encode(digest, 'hex')), 'utf-8')
    else:
        # codecs.encode needed for version before python3.5
        print(digest.hex())
    
    
if __name__ == '__main__':
    logging.basicConfig(level='WARNING')
    main(argv[1:])
            
