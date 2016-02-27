from math import log
from random import choice
from sys import stderr

# Size of buffers
BUFFER_SIZE = 512


class Steganography:
    def __init__(self, source_file=None, dest_file=None):
        """
        Class to hold the state of the steganography processing

        :param source_file:  Filename of the source file to encode in the mimicing
        :param dest_file:  Filename of the file to write the unstego'd data
        """
        self.data = []
        self.source_file = source_file
        self.dest_file = dest_file
        self.data = []
        self.done_encoding = False

        self.source = None
        self.dest = None
        if source_file:
            self.source = open(source_file, 'rb')
        if dest_file:
            self.dest = open(dest_file, 'wb')

    def get_bits(self, n):
        """
        Gets a specified number of bits from the source file stream.

        :param n:  The number of bits to retrieve
        :return:  An array of those bits.  [] once no bits remain
        """
        if len(self.data) < n:
            self.data.extend(to_bits(self.source.read(512)))

        bits = self.data[0:min(n, len(self.data))]
        self.data = self.data[min(n, len(self.data)):]
        return bits

    def add_bits(self, bits):
        """
        Add bits recovered from the reverse steganogtraphy process to the data buffer
        :param bits:
        :return:
        """
        self.data.extend(bits)

        # Periodically write out the data buffer to the file.
        # Only do this when the data lines up with byte boundaries
        if len(self.data) > BUFFER_SIZE and len(self.data) % 8 == 0:
            self.dest.write(from_bits(self.data))
            self.data = []

    def stego_choice(self, homoglyph):
        """
        Choose the next mimic character based on the data to encode

        :param homoglyph:  The current homoglyph that can be replaced
        :return:  The mimicked character
        """

        # Short circuit when there is no more data to encode
        if self.done_encoding:
            if homoglyph.fwd:
                return choice(homoglyph.fwd)
            return homoglyph.ascii

        # Get the number of options for this character.
        #
        # If there are fewer than 2, no data can be encoded so skip mimicking
        # this character and return the ascii
        options = len(homoglyph.fwd)
        if options < 2:
            return homoglyph.ascii

        # Determine how many bits of data this mimicking can encode
        bits_available = int(log(options, 2))
        to_encode = self.get_bits(bits_available)

        if to_encode:
            # There is data to encode, convert it to a character index
            bin_choice = "".join([str(x) for x in to_encode])

            # When the end of encoding data is reached and there are fewer
            # bits than can be encoded by this character, the end of the string
            # needs to be padded with 0s.  This prevents those 0s from being
            # inserted at the beginning of this character's decoding.
            #
            # The extra 0s are truncated because they will not line up with the
            # 8-bit byte boundary.
            if bits_available != len(to_encode):
                bin_choice += "0" * (bits_available - len(to_encode))

            int_choice = int(bin_choice, 2)
            return homoglyph.fwd[int_choice]
        else:
            if 2 ** bits_available < options:
                self.done_encoding = True
                return choice(homoglyph.fwd[2 ** bits_available:])
            else:
                return homoglyph.ascii

    def unstego(self, char, homoglyph):
        """
        Reverses the steganography encoding of stego_choice

        :param char:  the char to recover
        :param homoglyph:  the matching homoglyph
        :return: None
        """

        if not self.done_encoding:
            # Not all characters were replaced with homoglyphs
            if char in homoglyph.fwd:

                # Determine if there was a character choice outside the allowed range.
                # This indicates that there is no more data to recover and the rest of
                # the substitutions are cosmetic only.
                bits_available = int(log(len(homoglyph.fwd), 2))
                index = homoglyph.fwd.index(char)
                if index >= 2 ** bits_available:
                    self.done_encoding = True
                else:
                    bits_raw = bin(index)[2:]
                    # Pad the leading zeros to ensure the right bits are recorded.
                    bits = [0] * (bits_available - len(bits_raw)) + [int(d) for d in bits_raw]
                    self.add_bits(bits)

    def close(self):
        """
        Finish up processing the stego files
        """
        if self.source:
            if len(self.get_bits(1)) == 1:
                stderr.write("\nWARNING:  Not all data encoded.  Try a larger file or higher -m value\n")
            self.source.close()
        if self.dest:
            self.dest.write(from_bits(self.data))
            self.dest.flush()
            self.dest.close()


def to_bits(s):
    """
    Convert a string to a list of bits

    :param s: The string to convert
    :return: A list of bits (as integers) representing the string
    """
    result = []
    for c in s:
        bits = bin(ord(c))[2:] if isinstance(c, str) else bin(c)[2:]
        bits = '00000000'[len(bits):] + bits
        result.extend([int(b) for b in bits])
    return result


def from_bits(bits):
    """
    Converts a series of bits back into a string

    :param bits: The bits to convert
    :return:  The string represented by the bits
    """
    chars = []
    # extra bits are ignored.
    for b in range(int(len(bits) / 8)):
        byte = bits[b*8:(b+1)*8]
        chars.append(chr(int(''.join([str(bit) for bit in byte]), 2)))

    assembled = ''.join(chars)
    return assembled.encode('latin-1')
