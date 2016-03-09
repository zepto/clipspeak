#!/usr/bin/env python
# vim: sw=4:ts=4:sts=4:fdm=indent:fdl=0:
# -*- coding: UTF8 -*-
#
# An object for using espeak_text for 'playing' text.
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


""" Play espeak audio data to alsa.

"""

from multiprocessing import Process, Manager, Pipe
from io import SEEK_SET, SEEK_CUR, SEEK_END
from functools import wraps as functools_wraps
from time import sleep as time_sleep

from musio.alsa_io import Alsa as AudioDevice

from .espeak_text import EspeakText


class Reader(object):
    """ Play audio files.

    """

    def __init__(self):
        """ Player(text, **kwargs) -> Speak text.

        """

        self._text = ''

        # Setup the msg_dict for sending messages to the child process.
        self._msg_dict = Manager().dict()

        # Create a pipe for sending and receiving messages.
        self._control_conn, self._player_conn = Pipe()

    def __str__(self) -> str:
        """ The information about the open file.

        """

        return self._text

        # Wait for the stream to open.
        while 'info' not in self._msg_dict: pass

        # Return the info string.
        return self._msg_dict.get('info', '')

    def __repr__(self) -> str:
        """ __repr__ -> Returns a python expression to recreate this instance.

        """

        repr_str = ''  # "filename='%(_filename)s'" % self.__dict__

        return '%s(%s)' % (self.__class__.__name__, repr_str)

    def __enter__(self):
        """ Provides the ability to use pythons with statement.

        """

        try:
            return self
        except Exception as err:
            print(err)
            return None

    def __exit__(self, exc_type, exc_value, traceback):
        """ Stop playback when finished.

        """

        try:
            self.stop()
            self._control_conn.close()
            self._player_conn.close()
            return not bool(exc_type)
        except Exception as err:
            print(err)
            return False

    def __del__(self):
        """ Stop playback before deleting.

        """

        pass

    def __len__(self):
        """ The length of the file if it has one.

        """

        return self.length

    def playing_wrapper(func):
        """ Wrap methods and only call them if the stream is playing

        """

        @functools_wraps(func)
        def wrapper(self, *args, **kwargs):
            """ Check if stream is playing and if it is then call func
            otherwise print a message and exit.

            """

            if not self.playing:
                print("%(filename)s is not playing." % self._msg_dict)
                return None

            return func(self, *args, **kwargs)

        return wrapper

    def _play_proc(self, msg_dict: dict, pipe: Pipe):
        """ Player process

        """

        # Open the file to play.
        with EspeakText(**msg_dict) as fileobj:

            # Put the file info in msg_dict.
            # msg_dict['info'] = str(fileobj)
            msg_dict['length'] = fileobj.length

            # Open an audio output device that can handle the data from
            # fileobj.
            # with AudioDevice(rate=22050, channels=1) as device:

            device = AudioDevice(rate=22050, channels=1)
            try:

                # Set the default number of loops to infinite.
                fileobj.loops = msg_dict.get('loops', -1)

                # Initialize variable.
                buf = b'\x00' * device.buffer_size
                written = 0

                # Loop until stopped or nothing read or written.
                while msg_dict['playing'] and (buf or written):
                    # Keep playing if not paused.
                    if not msg_dict.get('paused', False):
                        # Re-open the device if it was closed.
                        if device.closed:
                            device = AudioDevice(rate=22050, channels=1)

                        # Read the next buffer full of data.
                        buf = fileobj.readline()

                        # Write buf.
                        written = device.write(buf)
                    else:
                        # Close the device when paused and sleep to
                        # open the audio for another process and
                        # save cpu cycles.
                        if not device.closed:
                            device.close()

                        time_sleep(0.05)

                        # Write a buffer of null bytes so the audio
                        # system can keep its buffer full.
                        # device.write(b'\x00' * device.buffer_size)

                    # Get and process any commands from the parent process.
                    if pipe.poll():
                        # Get the data into temp.
                        command = pipe.recv()

                        if 'getposition' in command:
                            pipe.send(fileobj.position)
                        elif 'setposition' in command:
                            fileobj.position = command['setposition']
            except Exception as err:
                print(err)
            finally:
                if not device.closed:
                    device.close()

        # Set playing to False for the parent.
        msg_dict['playing'] = False

    def read(self, text: str, **kwargs):
        """ Read the text.

        """

        self._text = text
        self._msg_dict['text'] = text
        self._msg_dict.update(kwargs)

        # After opening a new file stop the current one from playing.
        self.stop()

        # Pause it.
        self.pause()

        # Start it playing so seeking works.
        self.play()

    def play(self):
        """ play() -> Start playback.

        """

        if not self._msg_dict.get('playing', False):
            # Set playing to True for the child process.
            self._msg_dict['playing'] = True

            # Open a new process to play a file in the background.
            self._play_p = Process(target=self._play_proc,
                                   args=(self._msg_dict, self._player_conn))

            # Start the process.
            self._play_p.start()
        elif self._msg_dict.get('paused', True):
            # Un-pause if paused.
            self._msg_dict['paused'] = False

    def stop(self):
        """ stop() -> Stop playback.

        """

        if self._msg_dict.get('playing', False):
            # Stop playback.
            self._msg_dict['playing'] = False

            # Wait for the player process to stop.
            self._play_p.join()

            # Un-Pause.
            self._msg_dict['paused'] = False

    def pause(self):
        """ pause() -> Pause playback.

        """

        # Pause playback.
        self._msg_dict['paused'] = True

    @property
    def paused(self) -> bool:
        """ True if playback is paused.

        """

        return self._msg_dict.get('paused', False)

    @property
    def playing(self) -> bool:
        """ True if playing.

        """

        return self._msg_dict.get('playing', False)

    @property
    def length(self) -> int:
        """ Length of audio.

        """

        return self._msg_dict.get('length', 0)

    @property
    @playing_wrapper
    def position(self) -> int:
        """ Current position.

        """

        self._control_conn.send('getposition')
        return self._control_conn.recv()

    @position.setter
    @playing_wrapper
    def position(self, value: int):
        """ Set the current position.

        """

        self._control_conn.send({'setposition': int(value)})

    @playing_wrapper
    def tell(self) -> int:
        """ tell -> Returns the current position.

        """

        return self.position
