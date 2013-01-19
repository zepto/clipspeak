#!/usr/bin/env python
# vim: sw=4:ts=4:sts=4:fdm=indent:fdl=0:
# -*- coding: UTF8 -*-
#
# A text buffering object.
# Copyright (C) 2013 Josiah Gordon <josiahg@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


""" A text buffering object.

"""

import re


class Text(object):
    """ Wrap text file objects.

    """

    def __init__(self, text: str, sentence_endings: str='.!?'):
        """ Text(text) -> Just a regular file object.

        """

        self._text = text.encode()

        # Only read one line/sentence at a time.
        self._buffer_size = 1

        # Regex to match sentences.
        sentence_endings = '.*?[%s]' % re.escape(sentence_endings)
        re_flags = re.DOTALL | re.IGNORECASE | re.MULTILINE

        # Compile the sentence regex.
        sentence_regex = re.compile(sentence_endings.encode(), re_flags)

        # List of sentences in file
        sentence_list = sentence_regex.findall(self._text)

        # Check for sentence endings.
        if sentence_list:
            self._line_list = [sentence.decode() for sentence in sentence_list]
        elif self._text:
            self._line_list = self._text.decode().splitlines()
        else:
            self._line_list = []

        if self._line_list:
            # The length is the length of the line list.
            self._length = len(self._line_list)
        else:
            self._length = len(self._text)

        # Current index.
        self._index = 0

    def __repr__(self):
        """ __repr__ -> Returns a python expression to recreate this instance.

        """

        repr_str = "text='%(_text)s'" % self

        return '%s(%s)' % (self.__class__.__name__, repr_str)

    def readlines(self, count=-1) -> str:
        """ readlines(count=-1) -> Returns count lines/sentences if it can.

        """

        # Start index.
        slice_start = self._index

        # Return all the lines if count is -1.
        if count == -1:
            self._index = self._length
            return self._lines[slice_start:]

        # Calculate the last index to read to.
        slice_end = slice_start + count

        # Read count number of sentences if available.
        lines = ' '.join(self._line_list[slice_start:slice_end])

        # Increment the sentence index.
        self._index += count % ((self._length - slice_start) + count)

        return lines.replace('\n', ' ')

    def read(self, size: int) -> str:
        """ Return size or less ammount of text.

        """

        data = self.readlines(size)

        return data
