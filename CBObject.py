import struct
import hashlib
import time

class CBObject():
    # Header Fields
    header = bytearray()
    header_digest = bytearray()
    version = struct.pack("I", 1)
    previous_block_hash = bytearray()
    #merkle_root = bytearray(32)
    content_digest = bytearray()
    time_stamp = bytearray()
    difficulty_target = bytearray(b'\x20\x03\xa3\x0c')
    #nonce = bytearray(4)
    # Data Fields
    content_size = bytearray(4)
    content = bytearray()

    def setContent(self, data):
        self.content_size = struct.pack('I', len(data))
        self.content.extend(data)
        self.content_digest = self.sha256x2(self.content)
        self.time_stamp = struct.pack('I', int(time.time()))
        #print(self.time_stamp.hex())
        return

    def getContent(self):
        return self.content

    def farm(self, pbh):
        self.previous_block_hash.extend(pbh)

        # create the header bytearray
        self.header.extend(self.version)
        self.header.extend(self.previous_block_hash)
        self.header.extend(self.content_digest)
        self.header.extend(self.time_stamp)
        self.header.extend(self.difficulty_target)
        # nonce starts at 0
        nonce = 0
        self.header.extend(struct.pack('I', nonce))

        # get the difficulty target as a hex string
        dthex = self.getHexDifficulty();

        farmed = 0
        while not farmed:
            test_digest = self.sha256x2(self.header)
            #print(test_digest.hex())
            if (test_digest.hex() < dthex):
                self.header_digest = test_digest
                farmed = 1
            else:
                nonce += 1
                self.header[76:80] = struct.pack('I',nonce)

        #print(test_digest.hex(), dthex)
        return self.header_digest

    def parseFromBytes(self, bytes):
        total_size = struct.unpack('I', bytes[0:4])[0]
        #print(total_size)
        self.header = bytes[4:84]
        self.header_digest = self.sha256x2(self.header)
        self.version = self.header[0:4]
        self.previous_block_hash = self.header[4:36]
        self.content_digest = self.header[36:68]
        self.time_stamp = self.header[68:72]
        self.difficulty_target = self.header[72:76]
        self.nonce = self.header[76:80]
        self.content_size = bytes[84:88]
        cs = struct.unpack('I', self.content_size)[0]
        #print('content size: ', cs)
        self.content = bytes[88:88+cs]
        ch = self.sha256x2(self.content)

        if ch.hex() != self.content_digest.hex():
            print('Incorrect content hash')
        if total_size != 80 + 4 + cs:
            print('Incorrect total size')

        #print(self.content)

        return self

    def toBytes(self):
        block_array = bytearray(88)
        if len(self.header_digest) > 0:
            i_content_size = struct.unpack('I', self.content_size)[0]
            total_size = 80 + 4 + i_content_size
            #print('total size: ', total_size)
            block_array[0:4] = struct.pack('I', total_size)
            block_array[4:84] = self.header
            block_array[84:88] = self.content_size
            block_array.extend(self.content)
        return block_array

    def validateHeaderDigest(self):
        newDigest = self.sha256x2(self.header)
        return newDigest.hex() == self.header_digest.hex()

    def sha256x2(self, data):
        hashobj = hashlib.sha256(data)
        d1 = hashobj.digest()
        hashobj = hashlib.sha256(d1)
        digest = hashobj.digest()
        return digest

    def dumpHeader(self):
        print(self.header.hex())

    def getHexDifficulty(self):
        # Extract the exponent from the difficulty target
        # and convert to an integer
        eraw = bytearray(self.difficulty_target)
        eraw[1:4] = b'\x00\x00\x00'
        exponent = struct.unpack('I', eraw)[0] - 3

        # Calculate where the mantissa starts in the final dt
        # total length minus mant length minus exponent
        mantstart = 32 - 3 - exponent

        # Create the final difficult target
        dt = bytearray(32)
        dt[mantstart:mantstart+3] = self.difficulty_target[1:4]
        return dt.hex()

class CBObjectFactory:

    def createNew(self, data):
        block = CBObject()
        block.setContent(data)
        return block

    def loadFromBytes(self, bytes):
        block = CBObject()
        block.parseFromBytes(bytes)
        return block

    def addToChain(self):
        pass

    def loadFromChain(self, height):
        pass
