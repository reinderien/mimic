# coding=utf-8
from __future__ import print_function

from itertools import chain
from random import random, randrange
from sys import version_info

from mimic.steganography import Steganography

if version_info >= (3,):
    unichr = chr
    unicode = lambda s, e: s
    xrange = range


# Surrounding field for printing clarity
field = u'\u2591'

# source file
FILE = None

# List of all homoglyphs - named tuples with 'ascii' char, 'fwd' alternatives string for forward mimic mode, and 'rev'
# string of potentially non-universally-printable chars that should still be able to check or reverse back to ASCII
all_hgs = []

# Index dict of all homoglyphs for mimicking - key is any char, value is the named tuple described above
hg_index = {}


def fill_homoglyphs():
    """
    Use http://dev.networkerror.org/utf8/?start=0&end=255&cols=10&show_uni_hex=on
    with the stupid table width forced to auto.
    This dataset is for ASCII characters mapped to UTF-8 homoglyphs (some approximate).
    Some of the entries are also selected from the results of search(), below.

    Forward entries should stand a reasonable chance of rendering to look like their ASCII equivalent on most common
    fonts and systems.

    Reverse entries should exist for anything that could possibly be confused with an ASCII char, even if it doesn't
    render on some fonts and systems.

    If a character is deemed unprintable on some systems, don't delete it - move it from the fwd string to rev.
    """

    from collections import namedtuple
    Hgs = namedtuple('Hgs', ('ascii', 'fwd', 'rev'))

    all_hgs.extend(Hgs(*t) for t in (
        (' ', u'\u00A0\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200A\u202F\u205F', u'\u3000'),
        ('!', u'\uFF01\u01C3\u2D51\uFE15\uFE57', u'\u119D'),
        ('"', u'\uFF02', u'\u030E\u17C9'),
        ('#', u'\uFF03\uFE5F', u''),
        ('$', u'\uFF04\uFE69', u''),
        ('%', u'\uFF05\u066A\u2052\uFE6A', u''),
        ('&', u'\uFF06\uFE60', u''),
        ("'", u'\uFF07\u02B9\u0374', u'\u030D'),
        ('(', u'\uFF08\uFE59', u'\u207D\u208D\u27EE'),
        (')', u'\uFF09\uFE5A', u'\u207E\u208E\u27EF'),
        ('*', u'\uFF0A\u22C6\uFE61', u''),
        ('+', u'\uFF0B\u16ED\uFE62', u'\u207A\u208A'),
        (',', u'\uFF0C\u02CF\u16E7\u201A', u'\uFE10\uFE50\u0317\u0326'),
        ('-', u'\uFF0D\u02D7\u2212\u23BC\u2574\uFE63',
         u'\u207B\u208B\u0335\u1680\u174D\u1806\u1C7C\u23AF\u2CBB\u30FC\u3127'),
        ('.', u'\uFF0E\u2024', u'\uFE52\u0323'),
        ('/', u'\uFF0F\u1735\u2044\u2215\u29F8', u'\u0338\u2CC6\u3033'),
        ('0', u'', u'\u2070\u2080\u24EA\uFF10\u1C50'),
        ('1', u'', u'\u00B9\u2081\u2460\uFF11'),
        ('2', u'\u14BF', u'\u00B2\u2082\u2461\uFF12'),
        ('3', u'\u01B7\u2128', u'\u00B3\u2083\u2462\uFF13\u1883\u2CC4\u2CCC\u2CCD'),
        ('4', u'\u13CE', u'\u2074\u2084\u2463\uFF14'),
        ('5', u'', u'\u2075\u2085\u2464\uFF15'),
        ('6', u'\u13EE', u'\u2076\u2086\u2465\uFF16'),
        ('7', u'', u'\u2077\u2087\u2466\uFF17'),
        ('8', u'', u'\u2078\u2088\u2467\uFF18'),
        ('9', u'\u13ED', u'\u2079\u2089\u2468\uFF19'),
        (':', u'\uFF1A\u02D0\u02F8\u0589\u1361\u16EC\u205A\u2236\u2806\uFE13\uFE55',
         u'\u05C3\u17C7\u17C8\u1804\u1C7A\uFE30'),
        (';', u'\uFF1B\u037E\uFE14\uFE54', u''),
        ('<', u'\uFF1C\u02C2\u2039\u227A\u276E\u2D66\uFE64', u'\u3031\u3111'),
        ('=', u'\uFF1D\u2550\u268C\uFE66', u'\u207C\u208C\u30A0'),
        ('>', u'\uFF1E\u02C3\u203A\u227B\u276F\uFE65', u''),
        ('?', u'\uFF1F\uFE16\uFE56', u''),
        ('@', u'\uFF20\uFE6B', u''),
        ('A', u'\u0391\u0410\u13AA', u'\u1D2C\u24B6\uFF21'),
        ('B', u'\u0392\u0412\u13F4\u15F7\u2C82', u'\u1D2E\u212C\u24B7\uFF22'),
        ('C', u'\u03F9\u0421\u13DF\u216D\u2CA4', u'\u2102\u212D\u24B8\uFF23'),
        ('D', u'\u13A0\u15EA\u216E', u'\u1D30\u2145\u24B9\uFF24'),
        ('E', u'\u0395\u0415\u13AC', u'\u1D31\u2130\u24BA\uFF25'),
        ('F', u'\u15B4', u'\u2131\u24BB\uFF26'),
        ('G', u'\u050C\u13C0', u'\u1D33\u24BC\uFF27'),
        ('H', u'\u0397\u041D\u12D8\u13BB\u157C\u2C8E', u'\u1D34\u210B\u210C\u210D\u24BD\uFF28'),
        ('I', u'\u0399\u0406\u2160', u'\u1D35\u2110\u2111\u24BE\uFF29'),
        ('J', u'\u0408\u13AB\u148D', u'\u1D36\u24BF\uFF2A'),
        ('K', u'\u039A\u13E6\u16D5\u212A\u2C94', u'\u1D37\u24C0\uFF2B'),
        ('L', u'\u13DE\u14AA\u216C', u'\u1D38\u2112\u24C1\uFF2C\u2CD0\u31C4'),
        ('M', u'\u039C\u03FA\u041C\u13B7\u216F', u'\u1D39\u2133\u24C2\uFF2D'),
        ('N', u'\u039D\u2C9A', u'\u1D3A\u2115\u24C3\uFF2E'),
        ('O', u'\u039F\u041E\u2C9E', u'\u1D3C\u24C4\uFF2F\u1C5B'),
        ('P', u'\u03A1\u0420\u13E2\u2CA2', u'\u1D3E\u2119\u24C5\uFF30'),
        ('Q', u'\u051A\u2D55', u'\u211A\u24C6\uFF31\u10B3'),
        ('R', u'\u13A1\u13D2\u1587', u'\u1D3F\u211B\u211C\u211D\u24C7\uFF32'),
        ('S', u'\u0405\u13DA', u'\u24C8\uFF33\u10BD'),
        ('T', u'\u03A4\u0422\u13A2', u'\u1D40\u24C9\uFF34'),
        ('U', u'', u'\u1D41\u24CA\uFF35'),
        ('V', u'\u13D9\u2164', u'\u24CB\uFF36'),
        ('W', u'\u13B3\u13D4', u'\u1D42\u24CC\uFF37'),
        ('X', u'\u03A7\u0425\u2169\u2CAC', u'\u24CD\uFF38'),
        ('Y', u'\u03A5\u2CA8', u'\u03D2\u24CE\uFF39'),
        ('Z', u'\u0396\u13C3', u'\u2124\u24CF\uFF3A'),
        ('[', u'\uFF3B', u''),
        ('\\', u'\uFF3C\u2216\u29F5\u29F9\uFE68', u'\u3035'),
        (']', u'\uFF3D', u''),
        ('^', u'\uFF3E\u02C4\u02C6\u1DBA\u2303', u'\u0302'),
        ('_', u'\uFF3F\u02CD\u268A', u'\u0331\u0320\uFE58'),
        ('`', u'\uFF40\u02CB\u1FEF\u2035', u'\u0300'),
        ('a', u'\u0251\u0430', u'\u00AA\u1D43\u1D45\u2090\u24D0\uFF41'),
        ('b', u'', u'\u1D47\u24D1\uFF42'),
        ('c', u'\u03F2\u0441\u217D', u'\u1D9C\u24D2\uFF43'),
        ('d', u'\u0501\u217E', u'\u1D48\u2146\u24D3\uFF44'),
        ('e', u'\u0435\u1971', u'\u1D49\u2091\u212F\u2147\u24D4\uFF45\u19C9'),
        ('f', u'', u'\u1DA0\u24D5\uFF46'),
        ('g', u'\u0261', u'\u1D4D\u1DA2\u210A\u24D6\uFF47'),
        ('h', u'\u04BB', u'\u02B0\u210E\u24D7\uFF48'),
        ('i', u'\u0456\u2170', u'\u1D62\u2071\u2139\u2148\u24D8\uFF49'),
        ('j', u'\u03F3\u0458', u'\u02B2\u2149\u24D9\u2C7C\uFF4A'),
        ('k', u'', u'\u1D4F\u24DA\uFF4B'),
        ('l', u'\u217C', u'\u02E1\u2113\u24DB\uFF4C'),
        ('m', u'\u217F', u'\u1D50\u24DC\uFF4D'),
        ('n', u'\u1952', u'\u207F\u24DD\uFF4E'),
        ('o', u'\u03BF\u043E\u0D20\u2C9F', u'\u00BA\u1D52\u2092\u2134\u24DE\uFF4F\u0CE6\u0D66\u199E\u19D0'),
        ('p', u'\u0440\u2CA3', u'\u1D56\u24DF\uFF50'),
        ('q', u'', u'\u24E0\uFF51'),
        ('r', u'', u'\u02B3\u1D63\u24E1\uFF52'),
        ('s', u'\u0455', u'\u02E2\u24E2\uFF53'),
        ('t', u'', u'\u1D57\u24E3\uFF54'),
        ('u', u'\u1959\u222A', u'\u1D58\u1D64\u24E4\uFF55'),
        ('v', u'\u1D20\u2174\u2228\u22C1', u'\u1D5B\u1D65\u24E5\u2C7D\uFF56'),
        ('w', u'\u1D21', u'\u02B7\u24E6\uFF57'),
        ('x', u'\u0445\u2179\u2CAD', u'\u02E3\u2093\u24E7\uFF58'),
        ('y', u'\u0443\u1EFF', u'\u02B8\u24E8\uFF59'),
        ('z', u'\u1D22', u'\u1DBB\u24E9\uFF5A\u1901'),
        ('{', u'\uFF5B\uFE5B', u''),
        ('|', u'\uFF5C\u01C0\u16C1\u239C\u239F\u23A2\u23A5\u23AA\u23AE\uFFE8',
         u'\uFE33\u0846\u1175\u20D2\u2F01\u3021\u4E28\uFE31'),
        ('}', u'\uFF5D\uFE5C', u''),
        ('~', u'\uFF5E\u02DC\u2053\u223C', u'\u301C')
    ))

    hg_index.update({c: hgs for hgs in all_hgs for c in hgs.ascii + hgs.fwd + hgs.rev})


def is_ascii(char):
    return ord(' ') <= ord(char) <= ord('~')


def get_writer():
    """
    :return: A codec writer for stdout. Necessary for output piping to work.
    """
    from codecs import getwriter
    from sys import stdout

    if version_info >= (3,):
        return stdout
    return getwriter(stdout.encoding or 'utf-8')(stdout)


def listing():
    """
    Show a list of all known homoglyphs
    """
    out = get_writer()
    for hgs in all_hgs:
        out.write(hgs.ascii + ':')
        if hgs.fwd:
            out.write(' fwd ')
            for c in hgs.fwd:
                out.write(field + c)
            out.write(field)
        if hgs.rev:
            out.write(' rev ')
            for c in hgs.rev:
                out.write(field + c)
            out.write(field)
        out.write('\n')


def explain(char):
    """
    Show an explanation of all known homoglyphs for the given ASCII char
    :param char: An ASCII char to explain
    """
    if char not in hg_index:
        print('No homoglyphs.')
        return

    try:
        import unicodedata
    except ImportError:
        print('Install docutils.')
        return

    out = get_writer()

    out.write('Char\t%6s %20s %11s Cat Name\n' % ('Point', 'Normal', 'Rev/fwd/asc'))

    hgs = hg_index[char]
    for hg in hgs.ascii + hgs.fwd + hgs.rev:
        norms = ''
        for form in ('NFC', 'NFKC', 'NFD', 'NFKD'):
            h = unicodedata.normalize(form, hg)
            if h == hgs.ascii:
                if norms:
                    norms += ' '
                norms += form

        fwd_rev = ''
        if hg not in hgs.rev:
            fwd_rev += 'F'
        if hg in hgs.ascii:
            fwd_rev += 'A'
        else:
            fwd_rev += 'R'

        out.write(' %(field)c%(hg)c%(field)c\t'
                  'U+%(point)04X %(norms)20s %(fwdrev)11s %(cat)3s %(name)s\n' % {
                      'field': field,
                      'hg': hg,
                      'point': ord(hg),
                      'norms': norms,
                      'fwdrev': fwd_rev,
                      'cat': unicodedata.category(hg),
                      'name': unicodedata.name(hg, '<unnamed>')
                  })


def search():
    """
    (Not useful to the user) Troll the unicode DB for normalization matches, which are potentially homoglyphs.
    """
    try:
        import unicodedata
    except ImportError:
        print('Install docutils.')
        return

    out = get_writer()

    for point in xrange(ord('~') + 1, 0x10000):
        u = unichr(point)
        for form in ('NFC', 'NFKC', 'NFD', 'NFKD'):
            if u in hg_index:
                continue
            h = unicodedata.normalize(form, u)
            if len(h) == 1 and ord(h) != ord(u) and h in hg_index:
                out.write('%(ascii)c %(form)s->  %(hg)c\tU+%(point)04X %(cat)s/%(name)s\n' % {
                    'ascii': h,
                    'form': form,
                    'hg': u,
                    'point': ord(u),
                    'cat': unicodedata.category(u),
                    'name': unicodedata.name(u, '<unnamed>')
                })
                break


def pipe(read_line, replace, stego):
    """
    Pipe from input to output
    End with ctrl+C or EOF
    :param read_line: A function which returns the next line of input
    :param replace: A function to replace each char
    :param stego: A StegoHelper instance to manage the steganography
    """

    out = get_writer()

    # "for line in stdin" works for piped input but not keyboard input

    while True:
        try:
            line = read_line()
        except EOFError:
            return
        if line == '':
            return
        for c in line:
            if isinstance(c, int):
                c = chr(c)
            replacement = replace(c, stego)
            out.write(replacement)
        out.write('\n')


def pipe_mimic(read_line, hardness, stego):
    """
    Pipe from input to output, replacing chars with homoglyphs
    :param read_line: function to procide the next line of text to mimick
    :param hardness: Percent probability to replace a char
    :param stego: Steganography module to encode data in the mimicking
    """

    def replace(c, s):
        if isinstance(c, int):
            c = chr(c)
        if random() > hardness / 100. or c not in hg_index:
            return c
        hms = hg_index[c]

        # If there is a stego object, use that to choose the next character
        if s:
            return s.stego_choice(hms)

        # hms contains the current character. We've already decided, above, that this character should be replaced, so
        # we need to try and avoid that. Loop through starting at a random index.
        fwd = hms.ascii + hms.fwd
        start = randrange(len(fwd))
        for index in chain(xrange(start, len(fwd)), xrange(0, start)):
            if fwd[index] != c:
                return fwd[index]
        return c

    pipe(read_line, replace, stego)


def replace_reverse(c, stego):
    """
    Undo the damage to c
    """
    hgs = hg_index.get(c)
    if hgs:
        if stego:
            stego.unstego(c, hgs)
        return hgs.ascii
    return c


def replace_check(c, stego):
    """
    Replace non-ASCII chars with their code point
    """
    if ord(c) <= ord('~'):
        return c
    return '<%(orig)c:U+%(point)04X>' % {
        'orig': c,
        'point': ord(c)
    }


def parse():
    from optparse import OptionParser

    parser = OptionParser(usage='%prog [-h | -f [-m] [-e] | -r [-d] | -c [-d] | -x | -l]')
    parser.add_option('-f', '--forward', action='store_true',
                      help='mimic input to output (default)')
    parser.add_option('-r', '--reverse', action='store_true',
                      help='de-mimic input to output')
    parser.add_option('-c', '--check', action='store_true',
                      help='check input for suspicious chars, flag in output')
    parser.add_option('-e', '--encode', dest='source_steg_file',
                      help='encode this file as a hidden co-stream in output')
    parser.add_option('-d', '--decode', dest='dest_steg_file',
                      help='decode a hidden co-stream from input to this file')
    parser.add_option('-m', '--me-harder', dest='chance', type='float',
                      help='forward replacement percent, default 1')
    parser.add_option('-x', '--explain', dest='explain_char',
                      help="show a char's homoglyphs")
    parser.add_option('-l', '--list', action='store_true',
                      help='show all homoglyphs')
    parser.add_option('-s', '--source', dest='source_file',
                      help='mimic or demimic a source file instead of stdin')

    (options, args) = parser.parse_args()

    if not (options.forward or options.reverse or options.check or options.explain_char or options.list):
        options.forward = True

    present = set(o for o, v in vars(options).items() if v)

    def check_opts(opt, compat=None, req=None):
        req = req or set()
        compat = compat or req
        if opt in present:
            conflict = present - compat - {opt}
            if conflict:
                parser.error('%(opt)s given with incompatible options %(conflict)s' % {
                    'opt': opt,
                    'conflict': tuple(conflict)
                })
            if req and not present & req:
                parser.error('%(opt)s missing one of options %(req)s' % {
                    'opt': opt,
                    'req': tuple(req)
                })

    check_opts('forward', {'chance', 'source_steg_file', 'source_file'})
    check_opts('reverse', {'dest_steg_file', 'source_file'})
    check_opts('check', {'dest_steg_file', 'source_file'})
    check_opts('source_steg_file', {'forward', 'chance', 'source_file'}, {'forward'})
    check_opts('dest_steg_file', {'reverse', 'check', 'source_file'}, req={'reverse', 'check'})
    check_opts('chance', {'forward', 'source_steg_file', 'source_file'}, {'forward'})
    check_opts('explain_char')
    check_opts('list')

    if options.chance is None:
        options.chance = 1
    elif not 0 < options.chance <= 100:
        parser.error('bad percent value for -m')

    return options, args


def read_line_stdin():
    """
    read_line implementation drawing from stdin (default usage)
    :return:  Next line of input as a string
    """
    from sys import stdin

    if version_info >= (3,):
        return input()
    return raw_input().decode(stdin.encoding or 'utf-8')


def create_read_line_file(file_name):
    """
    read_line implementation drawing from a file

    :param file_name:  The name of the file to read
    :return:  The next line of the file
    """
    global FILE
    FILE = open(file_name, "rb")
    def read_line_file():
        return FILE.readline().decode("utf-8")
    return read_line_file


def main():
    try:
        (options, args) = parse()

        reader = read_line_stdin
        if options.source_file:
            reader = create_read_line_file(options.source_file)

        if options.forward:
            stego = Steganography(source_file=options.source_steg_file)
            pipe_mimic(reader, options.chance, stego)
            stego.close()
        elif options.reverse:
            stego = Steganography(dest_file=options.dest_steg_file)
            pipe(reader, replace_reverse, stego)
            stego.close()
        elif options.check:
            stego = Steganography()
            pipe(reader, replace_check, stego)
        elif options.explain_char:
            explain(unicode(options.explain_char, 'utf-8'))
        elif options.list:
            listing()
        else:
            raise Exception('No options parsed')
    except KeyboardInterrupt:
        pass


fill_homoglyphs()
