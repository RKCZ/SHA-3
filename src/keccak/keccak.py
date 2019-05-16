BYTE_SIZE = 8
INT_SIZE = 64
ROUND_COUNT = 24

BYTE_1 = 0x80

'''
rotates 
'''
def rotateLeft(a, n):
    return ((a >> (INT_SIZE - (n % INT_SIZE))) + (a << (n % INT_SIZE))) % (1 << INT_SIZE)


def KeccakRound(lanes):
    R = 1
    for _ in range(ROUND_COUNT):
        C = [lanes[x][0] ^ lanes[x][1] ^ lanes[x][2] ^ lanes[x][3] ^ lanes[x][4] for x in range(5)]
        D = [C[(x + 4) % 5] ^ rotateLeft(C[(x + 1) % 5], 1) for x in range(5)]
        lanes = [[lanes[x][y] ^ D[x] for y in range(5)] for x in range(5)]
        # ρ and π
        (x, y) = (1, 0)
        current = lanes[x][y]
        for t in range(ROUND_COUNT):
            (x, y) = (y, (2 * x + 3 * y) % 5)
            (current, lanes[x][y]) = (lanes[x][y], rotateLeft(current, (t + 1) * (t + 2) // 2))
        # χ
        for y in range(5):
            T = [lanes[x][y] for x in range(5)]
            for x in range(5):
                lanes[x][y] = T[x] ^ ((~T[(x + 1) % 5]) & T[(x + 2) % 5])
        # ι
        for j in range(7):
            R = ((R << 1) ^ ((R >> 7) * 0x71)) % 256
            if (R & 2):
                lanes[0][0] = lanes[0][0] ^ (1 << ((1 << j) - 1))
    return lanes


def load(b):
    return sum((b[i] << (BYTE_SIZE * i)) for i in range(BYTE_SIZE))


def store(a):
    return list((a >> (BYTE_SIZE * i)) % 256 for i in range(BYTE_SIZE))


def KeccakF(state):
    lanes = [[load(state[BYTE_SIZE * (x + 5 * y):BYTE_SIZE * (x + 5 * y) + BYTE_SIZE]) for y in range(5)] for x in range(5)]
    lanes = KeccakRound(lanes)
    state = bytearray(200)
    for x in range(5):
        for y in range(5):
            state[BYTE_SIZE * (x + 5 * y):BYTE_SIZE * (x + 5 * y) + BYTE_SIZE] = store(lanes[x][y])
    return state


def KeccakSponge(capacity, inputBytes, delimitedSuffix, outputByteLen, bitLength=1600):
    rate = bitLength - capacity
    bitLengthInBytes = bitLength // BYTE_SIZE
    rateInBytes = rate // BYTE_SIZE
    
    outputBytes = bytearray()
    
    # create Keccak state
    state = bytearray([0 for i in range(bitLengthInBytes)])
    blockSize = 0
    
    if (((rate % BYTE_SIZE) != 0)):
        raise ValueError("rate not divisible into bytes")
    inputOffset = 0
    # absorb
    while(inputOffset < len(inputBytes)):
        blockSize = min(len(inputBytes) - inputOffset, rateInBytes)
        for i in range(blockSize):
            
            # xor current state with absorbing message
            state[i] = state[i] ^ inputBytes[i + inputOffset]
        inputOffset = inputOffset + blockSize
        if (blockSize == rateInBytes):
            state = KeccakF(state)
            blockSize = 0
    # padding
    state[blockSize] = state[blockSize] ^ delimitedSuffix
    if (((delimitedSuffix & BYTE_1) != 0) and (blockSize == (rateInBytes - 1))):
        state = KeccakF(state)
    state[rateInBytes - 1] = state[rateInBytes - 1] ^ BYTE_1
    state = KeccakF(state)
    # squeeze
    while(outputByteLen > 0):
        blockSize = min(outputByteLen, rateInBytes)
        outputBytes = outputBytes + state[0:blockSize]
        outputByteLen = outputByteLen - blockSize
        if (outputByteLen > 0):
            state = KeccakF(state)
            
    return outputBytes


def SHA3(inputBytes, hashLength):
    # check received hash length is supported
    validLengths = [224, 256, 384, 512]
    if hashLength not in validLengths:
        raise ValueError("{} is not a supported hash length".format(hashLength))
    
    return KeccakSponge((hashLength * 2), inputBytes, 0x06, (hashLength // BYTE_SIZE))
