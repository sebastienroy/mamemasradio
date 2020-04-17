#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: Sebastien Roy
"""

import unittest
import time

from scrollingtext import ScrollingText

class test_ScrollingText(unittest.TestCase):

    def setUp(self):
        self._current_text = ""

    def text_function(self):
        return "test that is very long"

    def text_callback(self, originator, value):
        self._current_text = value
        
    def test_initial_value(self):
        """ This tests the initial value of the output text
        """
        scroll_text = ScrollingText(self.text_function, self.text_callback, 5,
                                    refresh_rate=0, scroll_begin_delay=0.1, 
                                    scroll_end_delay=0.05, scroll_rate=0.01)
        # check that the callback is not called at the initialization
        self.assertEqual(self._current_text, "")

        scroll_text.start()
        # the text is now the 5 first letters of the given text
        # no wait is necessary to give the text
        self.assertEqual(self._current_text, "test ")
        scroll_text.stop()
       

    def test_text_lenght(self):
        """ This checks that, one initialized, the length of the output text
            is always the same
        """
        scroll_text = ScrollingText(self.text_function, self.text_callback, 5,
                                    refresh_rate=0, scroll_begin_delay=0.1, 
                                    scroll_end_delay=0.05, scroll_rate=0.01)
        scroll_text.start()
        self.assertEqual(len(self._current_text), 5)
        time.sleep(0.1)
        self.assertEqual(len(self._current_text), 5)
        print(self._current_text)
        time.sleep(0.1)
        self.assertEqual(len(self._current_text), 5)
        print(self._current_text)
        scroll_text.stop()

    def test_restart(self):
        """ This checks that a scrolling text can be stopped and restarted
        """
        scroll_text = ScrollingText(self.text_function, self.text_callback, 5,
                                    refresh_rate=0, scroll_begin_delay=0.1, 
                                    scroll_end_delay=0.05, scroll_rate=0.01)
        scroll_text.start()
        print("started")
        time.sleep(0.1)
        scroll_text.stop()
        print("stopped")
        time.sleep(0.1)
        scroll_text.start()
        print("started")
        time.sleep(0.1)
        scroll_text.stop()
        print("stopped")
