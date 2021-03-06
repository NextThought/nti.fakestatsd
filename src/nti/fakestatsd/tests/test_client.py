#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

import doctest
import os
import unittest

from hamcrest import assert_that
from hamcrest import contains

from hamcrest import has_length
from hamcrest import has_properties
from hamcrest import has_property


from .. import FakeStatsDClient as MockStatsDClient

from ..metric import METRIC_COUNTER_KIND
from ..metric import METRIC_GAUGE_KIND
from ..metric import METRIC_SET_KIND
from ..metric import METRIC_TIMER_KIND

class TestMockStatsDClient(unittest.TestCase):

    def setUp(self):
        self.client = MockStatsDClient()

    def test_tracks_metrics(self):
        self.client.incr('mycounter')
        self.client.gauge('mygauge', 5)
        self.client.timing('mytimer', 3003)

        assert_that(self.client, has_length(3))

        counter, gauge, timer = self.client.metrics

        assert_that(counter, has_properties('name', 'mycounter',
                                            'value', '1',
                                            'kind', METRIC_COUNTER_KIND))

        assert_that(gauge, has_properties('name', 'mygauge',
                                          'value', '5',
                                          'kind', METRIC_GAUGE_KIND))

        assert_that(timer, has_properties(
            'name', 'mytimer',
            'value', '3003',
            'kind', METRIC_TIMER_KIND
        ))

    def test_clear(self):
        self.client.incr('mycounter')
        assert_that(self.client, has_length(1))

        self.client.clear()
        assert_that(self.client, has_length(0))


    def test_tracks_multimetrics(self):
        packet = 'gorets:1|c\nglork:320|ms\ngaugor:333|g\nuniques:765|s'
        self.client._send(packet)

        assert_that(self.client, has_length(4))
        assert_that(self.client.packets, contains(packet))

        assert_that(self.client.metrics, contains(has_property('kind', METRIC_COUNTER_KIND),
                                                  has_property('kind', METRIC_TIMER_KIND),
                                                  has_property('kind', METRIC_GAUGE_KIND),
                                                  has_property('kind', METRIC_SET_KIND)))

def test_suite():
    root = this_dir = os.path.dirname(os.path.abspath(__file__))
    while not os.path.exists(os.path.join(root, 'setup.py')):
        prev, root = root, os.path.dirname(root)
        if root == prev:
            # Let's avoid infinite loops at root
            raise AssertionError('could not find my setup.py')
    docs = os.path.join(root, 'docs')

    optionflags = (
        doctest.NORMALIZE_WHITESPACE
        | doctest.ELLIPSIS
        | doctest.IGNORE_EXCEPTION_DETAIL
    )

    index_rst = os.path.join(root, 'README.rst')
    # Can't pass absolute paths to DocFileSuite, needs to be
    # module relative
    index_rst = os.path.relpath(index_rst, this_dir)

    return unittest.TestSuite((
        unittest.defaultTestLoader.loadTestsFromName(__name__),
        doctest.DocFileSuite(
            index_rst,
            optionflags=optionflags
        ),
    ))
