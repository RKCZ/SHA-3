#! /usr/bin/python
'''
Created on 10 May 2019

@author: kalivoda
'''
BYTE_SIZE = 8
INT_SIZE = 64
ROUND_COUNT = 24

BYTE_1 = 0x80


def rotateLeft(a, n):
    return ((a >> (INT_SIZE - (n % INT_SIZE))) + (a << (n % INT_SIZE))) % (1 << INT_SIZE)


def keccakRound(lanes):
    rc = 1
    for _ in range(ROUND_COUNT):
        C = [lanes[x][0] ^ lanes[x][1] ^ lanes[x][2] ^ lanes[x][3] ^ lanes[x][4] for x in range(5)]
        D = [C[(x + 4) % 5] ^ rotateLeft(C[(x + 1) % 5], 1) for x in range(5)]
        lanes = [[lanes[x][y] ^ D[x] for y in range(5)] for x in range(5)]
        # ro and pi
        (x, y) = (1, 0)
        current = lanes[x][y]
        for t in range(ROUND_COUNT):
            (x, y) = (y, (2 * x + 3 * y) % 5)
            (current, lanes[x][y]) = (lanes[x][y], rotateLeft(current, (t + 1) * (t + 2) // 2))
        # chi
        for y in range(5):
            T = [lanes[x][y] for x in range(5)]
            for x in range(5):
                lanes[x][y] = T[x] ^ ((~T[(x + 1) % 5]) & T[(x + 2) % 5])
        # iota
        for j in range(7):
            rc = ((rc << 1) ^ ((rc >> 7) * 0x71)) % 256
            if (rc & 2):
                lanes[0][0] = lanes[0][0] ^ (1 << ((1 << j) - 1))
    return lanes


# load bits in lane from state into single byte
def load(b):
    return sum((b[i] << (BYTE_SIZE * i)) for i in range(BYTE_SIZE))


# convert bits from single byte into list
def store(a):
    return list((a >> (BYTE_SIZE * i)) % 256 for i in range(BYTE_SIZE))


def keccakF(state):
    # create lanes from received state
    lanes = [[load(state[BYTE_SIZE * (x + 5 * y):BYTE_SIZE * (x + 5 * y) + BYTE_SIZE]) for y in range(5)] for x in range(5)]
    
    # run permutations on lanes
    lanes = keccakRound(lanes)
    state = bytearray(200)
    
    # put permutated lanes back into state
    for x in range(5):
        for y in range(5):
            state[BYTE_SIZE * (x + 5 * y):BYTE_SIZE * (x + 5 * y) + BYTE_SIZE] = store(lanes[x][y])
    return state


def keccakSponge(capacity, inputBytes, delimitedSuffix, outputByteLen, bitLength=1600):
    rate = bitLength - capacity
    bitLengthInBytes = bitLength // BYTE_SIZE
    rateInBytes = rate // BYTE_SIZE
    
    outputBytes = bytearray()
    
    # create Keccak state
    state = bytearray([0 for i in range(bitLengthInBytes)])
    blockSize = 0
    
    if (((rate % BYTE_SIZE) != 0)):
        raise ValueError("rate {} is not divisible into bytes".format(rate))
    inputOffset = 0
    # absorb
    while(inputOffset < len(inputBytes)):
        # if remaining input is smaller than rate
        blockSize = min(len(inputBytes) - inputOffset, rateInBytes)
        
        for i in range(blockSize):            
            # xor current state with absorbing message
            state[i] = state[i] ^ inputBytes[i + inputOffset]
            
            # increment offset
        inputOffset = inputOffset + blockSize
        if (blockSize == rateInBytes):
            state = keccakF(state)
            blockSize = 0
    # add sha3 specific padding to the end of input
    state[blockSize] = state[blockSize] ^ delimitedSuffix
    
    # sha3 remaining input
    if (blockSize == (rateInBytes - 1)):
        state = keccakF(state)
    state[rateInBytes - 1] = state[rateInBytes - 1] ^ BYTE_1
    state = keccakF(state)
    
    # squeeze output of given length
    while(outputByteLen > 0):
        blockSize = min(outputByteLen, rateInBytes)
        outputBytes = outputBytes + state[0:blockSize]
        outputByteLen = outputByteLen - blockSize
        if (outputByteLen > 0):
            state = keccakF(state)
            
    return outputBytes


def sha3(inputBytes, hashLength=224):
    # check received sha3 length is supported
    validLengths = [224, 256, 384, 512]
    if hashLength not in validLengths:
        raise ValueError("{} is not a supported sha3 length".format(hashLength))
    
    return keccakSponge((hashLength * 2), inputBytes, 0x06, (hashLength // BYTE_SIZE))
