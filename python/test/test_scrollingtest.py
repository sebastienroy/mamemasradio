#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 23 15:12:37 2018

@author: Sebastien Roy
"""

import unittest
import time
import logging


from scrollingtext import ScrollingText

class test_ScrollingText(unittest.TestCase):
    """ This is unitary tests for class ScrollingText
    """

    def setUp(self):
        """ Initialisation
        """
        self._current_text = ""
        self._text_counter = []
        logging.basicConfig(format='%(levelname)s:%(asctime)s:%(message)s',
                            level=logging.ERROR
                            )



    def text_function(self):
        return "test that is very long"

    def text_callback(self, originator, value):
        self._current_text = value

    def test_initial_value(self):
        """ This tests the initial value of the output text
        """
        print("---------------------------")
        print("Begining test initial value...")
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
        print("...end test initial value")

    def test_text_lenght(self):
        """ This checks that, one initialized, the length of the output text
            is always the same
        """
        print("---------------------------")
        print("Begining test text length...")
        scroll_text = ScrollingText(self.text_function, self.text_callback, 5,
                                    refresh_rate=0, scroll_begin_delay=0.1,
                                    scroll_end_delay=0.05, scroll_rate=0.01)
        scroll_text.start()
        self.assertEqual(len(self._current_text), 5)
        time.sleep(0.1)
        self.assertEqual(len(self._current_text), 5)
        time.sleep(0.1)
        self.assertEqual(len(self._current_text), 5)
        scroll_text.stop()
        print("... end test text length.")

    def test_restart(self):
        """ This checks that a scrolling text can be paused and resumed
        """
        print("---------------------------")
        print("Begining test restart...")
        scroll_text = ScrollingText(self.text_function, self.text_callback, 5,
                                    refresh_rate=0, scroll_begin_delay=0.05,
                                    scroll_end_delay=0.05, scroll_rate=0.01)

        # The text function returns "test that is very long"
        # So, at beginning, the text should start with "test"
        scroll_text.start()
        self.assertTrue(self._current_text.startswith("test"))

        # after 0.1 seconds, the text should have scrolled
        time.sleep(0.1)
        self.assertFalse(self._current_text.startswith("test"))

        # during the pause, the text should not change
        scroll_text.pause()
        paused_text = self._current_text
        time.sleep(0.1)
        self.assertEqual(paused_text, self._current_text)

        # once resumed, the text should change again
        # and the text should be reset to initial
        scroll_text.resume()
        self.assertTrue(self._current_text.startswith("test"))
        time.sleep(0.15)
        self.assertFalse(self._current_text.startswith("test"))

        scroll_text.stop()
        print("... end test restart.")

    def counting_callback(self, originator, value):
        #nanos = time.time_ns()
        nanos = time.time()
        self._text_counter.append((nanos, value))

    def count_text_function(self):
        return "0123456789"

    def test_count_and_time(self):
        """ This test mesures the time between the different updates of the text
        """
        print("---------------------------")
        print("Begining test count and time...")
        scroll_text = ScrollingText(self.count_text_function, self.counting_callback,
                                    5, refresh_rate=0, scroll_begin_delay=0.05,
                                    scroll_end_delay=0.07, scroll_rate=0.01)
        scroll_text.start()
        # The scroll text needs 0.2 = 0.05s + 5x0.01s + 0.07s to return to the beginning
        # So, it needs 0.27s to restart scrolling after the first cycle
        time.sleep(0.3)
        scroll_text.stop()

        # verify results
        full_text = self.count_text_function()
        self.assertGreaterEqual(len(self._text_counter), 7,
                                "The scrolling text should have changed at least 7 times.")

        t0 = self._text_counter[0][0]
        text = self._text_counter[0][1]
        self.assertEqual(text, full_text[0:5], "The initial text should be the first five characters of the text function")

        # Check first iteration
        t1 = self._text_counter[1][0]
        delta1 = t1 - t0
        self.assertAlmostEqual(delta1, 0.05,
                               msg="The first iteration is expecter after 0.05s",
                               delta=0.02)
        self.assertEqual(self._text_counter[1][1], full_text[1 : 6], "The text of the first iteration is expected to be \"12345\"")

        # check iteration from 2 to the end
        for i in range(2, 6):
            delta_n = self._text_counter[i][0] - self._text_counter[i - 1][0]
            text = self._text_counter[i][1]
            self.assertAlmostEqual(delta_n, 0.01, delta=0.002)
            self.assertEqual(text, full_text[i : i + 5])

        # check that the last iteration is longuer
        delta_last = self._text_counter[6][0] - self._text_counter[5][0]
        self.assertAlmostEqual(delta_last, 0.07, delta=0.02,
                               msg="The last iteration should last 0.07s")
        # Then, the new cycle begins
        delta_new = self._text_counter[7][0] - self._text_counter[6][0]
        self.assertAlmostEqual(delta_new, 0.05, delta=0.02)
        text_new = self._text_counter[6][1]
        self.assertEqual(text_new, full_text[0:5],
                         msg="The scrolling text should start an new cycle after 7 iterations")

        print("... end test restart.")
