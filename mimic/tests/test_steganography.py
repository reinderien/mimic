import os
import tempfile
import unittest

from mimic import Steganography, Hgs


class TestStego(unittest.TestCase):
    def binstr_to_list(self, string):
        return [int(d) for d in string.replace(" ", "")]

    def test_get_bits(self):
        date_file = tempfile.mkstemp()
        with open(date_file[1], 'w') as temp:
            temp.write("hello")
        stego = Steganography(source_file=date_file[1])

        try:
            self.assertEquals(self.binstr_to_list("01101000"), stego.get_bits(8))
            self.assertEquals(self.binstr_to_list("01100101 01101100 01101100 01101111"), stego.data)
            self.assertEquals(self.binstr_to_list("01100101 01101100 01101100 0110"), stego.get_bits(28))
            self.assertEquals(self.binstr_to_list("1111"), stego.data)
            self.assertEquals(self.binstr_to_list("1111"), stego.get_bits(4))
            self.assertEquals([], stego.data)
            self.assertEquals([], stego.get_bits(4))
            stego.data = self.binstr_to_list("1111")
            self.assertEquals(self.binstr_to_list("1111"), stego.get_bits(8))
            self.assertEquals([], stego.data)
            stego.close()
        finally:
            os.close(date_file[0])
            os.remove(date_file[1])

    def test_encodable_bits(self):
        self.assertEquals(0, Steganography.encodable_bits([]))
        self.assertEquals(0, Steganography.encodable_bits([0]))
        self.assertEquals(1, Steganography.encodable_bits([0, 1]))
        self.assertEquals(1, Steganography.encodable_bits([0, 1, 2]))
        self.assertEquals(2, Steganography.encodable_bits([0, 1, 2, 3]))
        self.assertEquals(2, Steganography.encodable_bits([0, 1, 2, 3, 4]))

    def test_encode(self):
        date_file = tempfile.mkstemp()
        with open(date_file[1], 'w') as temp:
            temp.write("j")  # 01101010

        stego = Steganography(source_file=date_file[1])
        self.assertTrue(stego.enabled)
        try:

            # Not enough choices, should pass through
            self.assertEquals('a', stego.stego_encode(Hgs('a', '1', '')))

            # Can encode 1 bit, should choose 1st (0)
            self.assertEquals('1', stego.stego_encode(Hgs('a', '12', '')))
            self.assertEquals(self.binstr_to_list("1101010"), stego.data)

            # Can encode 1 bit, should choose 2nd (1)
            self.assertEquals('2', stego.stego_encode(Hgs('a', '12', '')))
            self.assertEquals(self.binstr_to_list("101010"), stego.data)

            # Can encode 2 bits, should choose 3rd (10)
            self.assertEquals('3', stego.stego_encode(Hgs('a', '1234', '')))
            self.assertEquals(self.binstr_to_list("1010"), stego.data)

            # Can encode 2 bits, should choose 3rd (10)
            self.assertEquals('3', stego.stego_encode(Hgs('a', '1234', '')))
            self.assertEquals(self.binstr_to_list("10"), stego.data)

            # Can encode 3 bits, should choose 5th (100)
            self.assertEquals('5', stego.stego_encode(Hgs('a', '12345678', '')))
            self.assertEquals(self.binstr_to_list(""), stego.data)

            # Trying to encode end marker but not enough choices
            self.assertEquals('a', stego.stego_encode(Hgs('a', '1234', '')))
            self.assertFalse(stego.done_encoding)

            # Enough choices now
            self.assertEquals('5', stego.stego_encode(Hgs('a', '12345', '')))
            self.assertTrue(stego.done_encoding)

            # Choosing randomly for all future replacements
            self.assertEquals('1', stego.stego_encode(Hgs('a', '1', '')))

            # Should still work if there are no fwd choices
            self.assertEquals('a', stego.stego_encode(Hgs('a', '', '')))

        finally:
            stego.close()
            os.close(date_file[0])
            os.remove(date_file[1])

    def test_decode(self):
        data_file = tempfile.mkstemp()

        old_size = Steganography.BUFFER_SIZE
        stego = Steganography(dest_file=data_file[1])
        try:
            self.assertTrue(stego.enabled)
            stego.stego_decode('a', Hgs('a', '1234', ''))
            self.assertEquals([], stego.data)
            self.assertFalse(stego.done_encoding)

            stego.stego_decode('1', Hgs('a', '12', ''))
            self.assertEquals(self.binstr_to_list("0"), stego.data)
            stego.stego_decode('2', Hgs('a', '12', ''))
            self.assertEquals(self.binstr_to_list("01"), stego.data)
            stego.stego_decode('1', Hgs('a', '1234', ''))
            self.assertEquals(self.binstr_to_list("0100"), stego.data)
            stego.stego_decode('3', Hgs('a', '1234', ''))
            self.assertEquals(self.binstr_to_list("010010"), stego.data)
            stego.stego_decode('4', Hgs('a', '1234', ''))
            self.assertEquals(self.binstr_to_list("01001011"), stego.data)

            # Outside range of encodable bits so must be end
            stego.stego_decode('5', Hgs('a', '12345', ''))
            self.assertEquals(self.binstr_to_list("01001011"), stego.data)
            self.assertTrue(stego.done_encoding)

            Steganography.BUFFER_SIZE = 7
            # trigger a write
            stego.add_bits([])
            stego.dest.flush()
            with open(data_file[1], 'r') as written:
                self.assertEquals('K', written.read())

        finally:
            Steganography.BUFFER_SIZE = old_size
            stego.close()
            os.close(data_file[0])
            os.remove(data_file[1])

    def test_disabled(self):
        stego = Steganography()
        self.assertFalse(stego.enabled)


if __name__ == '__main__':
    unittest.main()
