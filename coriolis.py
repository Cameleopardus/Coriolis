
import multiprocessing
from multiprocessing import log_to_stderr
import logging
import atexit
import os

from twisted.internet import reactor
from twisted.internet import protocol
from twisted.internet import ssl
from twisted.words.protocols import irc

import settings
import worker as Worker


networks = settings.networks
from loader import Loader
import profiler
import signal
import threading

worker = Worker.init()
logger = log_to_stderr()
logger.setLevel(logging.INFO)
m = multiprocessing.Manager()


@atexit.register
def cleanup(signal, frame):
    stoppool = threading.Thread(target=worker.close())
    stoppool.daemon = True
    stoppool.start()
    print("Cleaning Up..")
    print("bye!")
    os._exit(0)

signal.signal(signal.SIGINT, cleanup)


def _parseModes(modes, params, paramModes=('', '')):

    if len(modes) == 0:
        raise IRCBadModes('Empty mode string')

    if modes[0] not in '+-':
        raise IRCBadModes('Malformed modes string: %r' % (modes,))

    changes = ([], [])

    direction = None
    count = -1
    for ch in modes:
        if ch in '+-':
            if count == 0:
                raise IRCBadModes('Empty mode sequence: %r' % (modes,))
            direction = '+-'.index(ch)
            count = 0
        else:
            param = None
            if ch in paramModes[direction]:
                try:
                    param = params.pop(0)
                except IndexError:
                    raise IRCBadModes('Not enough parameters: %r' % (ch,))
            changes[direction].append((ch, param))
            count += 1

    if count == 0:
        raise IRCBadModes('Empty mode sequence: %r' % (modes,))

    return changes


class Coriolis(irc.IRCClient):

    def connectionMade(self):
        irc.IRCClient.connectionMade(self)

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)
    f = protocol.ReconnectingClientFactory()
    f.protocol = irc

    def signedOn(self):

        network = self.factory.network

        if network['identity']['nickserv_pw']:
            self.msg('NickServ',
                     'IDENTIFY %s' % network['identity']['nickserv_pw'])

        for channel in network['autojoin']:
            print('join channel %s' % channel)
            self.join(channel)

    def irc_MODE(self, user, params):
        """
        Parse a server mode change message, altered to support slack irc gateway
        """
        channel, modes, args = params[0], params[1], params[2:]

        if modes[0] not in '-+':
            modes = '+' + modes

        if channel == self.nickname:
            # This is a mode change to our individual user, not a channel mode
            # that involves us.
            paramModes = self.getUserModeParams()
        else:
            paramModes = self.getChannelModeParams()

        try:
            added, removed = _parseModes(modes, args, paramModes)
        except IRCBadModes:
            log.err(None, 'An error occurred while parsing the following '
                          'MODE message: MODE %s' % (' '.join(params),))
        else:
            if added:
                modes, params = zip(*added)
                self.modeChanged(user, channel, True, ''.join(modes), params)

            if removed:
                modes, params = zip(*removed)
                self.modeChanged(user, channel, False, ''.join(modes), params)

    @profiler.time_execution
    def parseCommand(self, usr, msg, chan):

        plgname = msg.split()[0].replace("!", "")
        plugins = Loader()
        for plugin in plugins.load():
            plg = plugins.get(plugin)

            if msg.startswith(("!" + plugin["name"])):
                args = msg.replace(("!" + plugin["name"]), "")
                A, B = multiprocessing.Pipe()

                response = plg.do(args, pipe=B)
                print(response)
                self.msg(chan, response)
                A.close()

    def joined(self, channel):
        print('joined channel')

    def privmsg(self, user, channel, msg):
        print('[%s] <%s> %s' % (channel, user, msg))
        usr = user.split('!', 2)[0].replace('.', '')
        worker.do_work(self.parseCommand(usr, msg, channel))

    def alterCollidedNick(self, nickname):
        return nickname + '_'

    def _get_nickname(self):
        return self.factory.network['identity']['nickname']

    def _get_realname(self):
        return self.factory.network['identity']['realname']

    def _get_username(self):
        return self.factory.network['identity']['username']

    def _get_password(self):
        if self.factory.network['identity']['server_pw']:
            return self.factory.network['identity']['server_pw']
        else:
            return ""

    nickname = property(_get_nickname)
    realname = property(_get_realname)
    username = property(_get_username)
    password = property(_get_password)



class CoriolisFactory(protocol.ClientFactory):
    protocol = Coriolis

    def __init__(self, network_name, network):
        self.network_name = network_name
        self.network = network

    def clientConnectionLost(self, connector, reason):
        print('client connection lost')
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print('client connection failed')
        reactor.stop()


def start():
    try:
        for name in networks.keys():
            factory = CoriolisFactory(name, networks[name])

            host = networks[name]['host']
            port = networks[name]['port']

            if networks[name]['ssl']:

                reactor.connectSSL(host, port, factory, ssl.ClientContextFactory())
            else:
                reactor.connectTCP(host, port, factory)

        reactor.run()
    except (KeyboardInterrupt, SystemExit) as e:
        cleanup()
