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
    usageMsg = 'sha3.py [-o <outputFile>] [-h] [-l <hashLength>] <[-i <inputFile>] | [STDIN] | [message]>\n'
    helpMsg = 'Prints SHA-3 hash value of given input. By default 224-bit hashes are used. Other possible lengths are 256, 384 or 512.\n Possible input is file (specified by one of command options), STDIN or string specified as last command argument.\nBy default output is printed to STDOUT encoded as hexadecimal string. It can also be saved into given output file.'
    inputfile = ''
    readFromFile = False
    writeToFile = False
    outputfile = ''
    inputText = ''
    hashLength = 224

    try:
        opts, args = getopt(argv, "hi:o:l:", ["input=", "output=", "length="])
    except GetoptError:
        print(usageMsg)
        exit(2);

    for opt, arg in opts:
        if opt == '-h':
            print(usageMsg)
            print(helpMsg)
            exit()
        elif opt in ("-i", "--input"):
            inputfile = arg
            readFromFile = True
            
        elif opt in ("-o", "--output"):
            outputfile = arg
            writeToFile = True
        elif opt in ("-l", "--length"):
            try:
                hashLength = int(arg)
            except ValueError as e:
                exit(str(e))

    if readFromFile:    
        with open(inputfile, 'rb') as f:
            inputText = codecs.decode(f.read())
    else:
        if len(args) < 1:
            inputText = stdin.read()
        else:
            inputText = args[0]
            
    try:
        logging.debug("Input message = {}".format(inputText))
        digest = keccak.sha3(inputText.encode(), hashLength)
    except ValueError as e:
        exit("hashing failed: {}".format(str(e)))
        
    if writeToFile:
        with open(outputfile, 'wb') as f:
            f.write(digest)
    else:
        # codecs.encode needed for version before python3.5
        print(codecs.decode(codecs.encode(digest, 'hex'), 'utf-8'))
    
    
if __name__ == '__main__':
    logging.basicConfig(level='WARNING')
    main(argv[1:])
            
