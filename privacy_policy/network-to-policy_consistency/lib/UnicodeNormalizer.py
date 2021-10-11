#!/usr/bin/env python

# This file is a part of OVRseen <https://athinagroup.eng.uci.edu/projects/ovrseen/>.
# Copyright (c) 2021 UCI Networking Group.
#
# This file incorporates content from the HtmlToPlaintext repo <https://github.com/benandow/HtmlToPlaintext>.
#
# OVRseen is dual licensed under the MIT License and the GNU General Public
# License version 3 (GPLv3). This file is covered by the GPLv3. If this file
# get used, GPLv3 applies to all of OVRseen.
#
# See the LICENSE.md file along with OVRseen for more details.

import re
import unicodedata

mapping = {
            '\u2000' : ' ',
            '\u2001' : ' ',
            '\u2002' : ' ',
            '\u2003' : ' ',
            '\u2004' : ' ',
            '\u2005' : ' ',
            '\u2006' : ' ',
            '\u2007' : ' ',
            '\u2008' : ' ',
            '\u2009' : ' ',
            '\u200A' : ' ',
            '\u200B' : ' ',
            '\u200C' : '',
            '\u200D' : '',
            '\u200E' : ' ', #LRM
            '\u200F' : ' ', #RLM
            '\u2010' : '-',
            '\u2011' : '-',
            '\u2012' : '-',
            '\u2013' : '-',
            '\u2014' : '-',
            '\u2015' : '-',
            '\u2016' : '||',
            '\u2017' : '=',
            '\u2018' : '\'',
            '\u2019' : '\'',
            '\u201A' : ',',
            '\u201B' : '\'',
            '\u201C' : '"',
            '\u201D' : '"',
            '\u201E' : '"',
            '\u201F' : '"',
            '\u2020' : '', #cross
            '\u2021' : '', #double cross
            '\u2022' : '', #bulletpoint
            '\u2023' : '', #bullet arrow
            '\u2024' : '.', #dot
            '\u2025' : '..', #dot dot
            '\u2026' : '...', #dot dot dot
            '\u2027' : '.',
            '\u2028' : ' ',#LSEP
            '\u2029' : ' ',#RSEP
            '\u202A' : ' ',#LRE
            '\u202B' : ' ',#RLE
            '\u202C' : ' ',#PDF
            '\u202D' : ' ',#LRO
            '\u202E' : ' ',#RLO
            '\u202F' : ' ',
            '\u2030' : '%',
            '\u2031' : '%',
            '\u2032' : '\'',
            '\u2033' : '"',
            '\u2034' : '"',
            '\u2035' : '\'',
            '\u2036' : '"',
            '\u2037' : '"',
            '\u2038' : '^',
            '\u2039' : '<',
            '\u203A' : '>',
            '\u203B' : '*',
            '\u203C' : '!!',
            '\u203D' : '?',
            '\u203E' : '-',
            '\u203F' : '',
            '\u2040' : '',
            '\u2041' : '',
            '\u2042' : '',
            '\u2043' : '-',
            '\u2044' : '/',
            '\u2045' : '[',
            '\u2046' : ']',
            '\u2047' : '??',
            '\u2048' : '?!',
            '\u2049' : '!?',
            '\u204A' : '',
            '\u204B' : '',
            '\u204C' : '',
            '\u204D' : '',
            '\u204E' : '*',
            '\u204F' : ';',
            '\u2050' : '',
            '\u2051' : '',
            '\u2052' : '%',
            '\u2053' : '~',
            '\u2054' : '',
            '\u2055' : '*',
            '\u2056' : '',
            '\u2057' : '"',
            '\u2058' : '',
            '\u2059' : '',
            '\u205A' : ':',
            '\u205B' : '',
            '\u205C' : '',
            '\u205D' : '',
            '\u205E' : '',
            '\u205F' : ' ',
            '\u2060' : ' ',
            '\u2061' : ' ',
            '\u2062' : ' ',
            '\u2063' : ',',
            '\u2064' : ' ',
            '\u2065' : ' ',
            '\u2066' : ' ',
            '\u2067' : ' ',
            '\u2068' : ' ',
            '\u2069' : ' ',
            '\u206A' : ' ',
            '\u206B' : ' ',
            '\u206C' : ' ',
            '\u206D' : ' ',
            '\u206E' : ' ',
            '\u206F' : ' ',
            # Strip trademark, copyright, and registered symbols
            '\u00ae' : '',
            '\u2122' : '',
            '\u00a9' : '',
        }


def normalize(text):
    if type(text) == list:
        return [ normalize(t) for t in text ]
    for unicodeChar in mapping:
        text = re.sub(unicodeChar, mapping[unicodeChar], text, re.UNICODE)

    text = re.sub(r'\xa0', ' ', text)
    text = re.sub(r'\s+', ' ', text)# Remove multiple white space

    text = unicodedata.normalize('NFKD', text)  # unicode normalize
    text = re.sub(r'[\u0300-\u0362\u20D0-\u20E3]', '', text)  # remove accents from characters

    return text
