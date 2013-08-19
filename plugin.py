###
# Copyright (c) 2013, beerware
# All rights reserved.
#
#
###

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import supybot.ircmsgs as ircmsgs
import supybot.dbi as dbi
import random
from datetime import datetime

class PingusRecord(dbi.Record):
    __fields__ = [
            'nick',
            'by',
            'at',
            'ponged',
            ]

class DbiPingusDB(dbi.DB):
    Mapping = 'flat'
    Record = PingusRecord

    def __init__(self, *args, **kwargs):
        dbi.DB.__init__(self, *args, **kwargs)

    def addping(self, nick, msg):
        record = self.Record(nick=nick, by=msg.nick,
                at=msg.receivedAt)
        self.add(record)
        #super(self.__class__, self).add(record)
    def pong(self, nick, msg):
        result = [x for x in self if x.nick in msg.nick and x.by in nick and\
                not x.ponged]
        if result:
            result = result[0]
            record = self.Record(nick = result.nick, by = result.by,at =\
                    result.at, ponged = 1)
            self.set(result.id, record)
            return {
                    'nick':result.nick,
                    'by':result.by,
                    'at':result.at
                    }
        else:
            return {}

    def _clean(self):
        result = [x for x in self if not x.ponged]
        if result:
            for not_clean in result:
                self.remove(not_clean.id)

    def find_timeout(self):
        result = [x for x in self if not x.ponged]
        to_return = []
        for not_pong in result:
            time = datetime.now() - datetime.fromtimestamp(not_pong.at)
            if time.total_seconds() > 3600:
                to_return.append(not_pong)
        return to_return

PINGDB = plugins.DB('Pingus', {'flat': DbiPingusDB}) 


class Pingus(callbacks.Plugin):
    """Add the help for "@plugin help Pingus" here
    This should describe *how* to use this plugin."""
    def __init__(self, irc):
        self.__parent = super(Pingus, self)
        self.__parent.__init__(irc)
        self.db = PINGDB()
        self.db._clean()

    def doPrivmsg(self, irc, msg):
        channel = msg.args[0]
        self.timeout(irc, channel)
        if ircmsgs.isCtcp(msg) and not ircmsgs.isAction(msg):
            return
        #channel = msg.args[0]
        if irc.isChannel(channel):
            if ircmsgs.isAction(msg):
                text = ircmsgs.unAction(msg)
            else:
                text = msg.args[1]
            if 'ping' in text.lower():
                self.ping(irc, msg, channel, text)
            elif 'pong' in text.lower():
                self.pong(irc, msg, channel, text)

    def ping(self, irc, msg, channel, text):
        if 'solevis' in text.lower():
            irc.reply('On ne ping pas solevis !!')
            irc.reply("C'est solevis qui te ping !!")
        else:
            nick = text.split()[0][:-1]
            if not nick in irc.state.channels[channel].users:
                texte = "92 bytes from %s (%s): Destination Net\
Unreachable" % (nick,msg.nick)
                irc.sendMsg(ircmsgs.privmsg(channel, texte))
                irc.noReply()
            else:
                self.db.addping(nick, msg)

    def pong(self, irc, msg, channel, text):
        if 'solevis' in msg.nick.lower():
            irc.reply("HO MY GOD !! IS ALIIIIIVE !!")
        else:    
            now = datetime.now()
            nick = text.split()[0][:-1]
            ping = self.db.pong(nick, msg)
            if ping:
                time = now - datetime.fromtimestamp(ping['at'])
                texte = '64 bytes from %s: icmp_seq=0 ttl=64 time=%s s' %\
                        (msg.nick,time.total_seconds())
                irc.sendMsg(ircmsgs.privmsg(channel, texte))
                irc.noReply()

    def timeout(self, irc, channel):
        out = self.db.find_timeout()
        if out:
            for to_reply in out:
                texte = '%s : 36 bytes from %s: Time to live exceeded' % \
                        (to_reply.by, to_reply.nick)
                irc.sendMsg(ircmsgs.privmsg(channel, texte))
                irc.noReply()

            

Class = Pingus


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
