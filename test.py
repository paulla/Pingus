###
# Copyright (c) 2013, beerware
# All rights reserved.
#
#
###

from supybot.test import *

class PingusTestCase(PluginTestCase):
    plugins = ('Pingus',)

    def testPing(self):
        self.assertNotError('ping')

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
