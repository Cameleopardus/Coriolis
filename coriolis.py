__author__ = 'zen'
import multiprocessing
from multiprocessing import log_to_stderr
import logging
import atexit

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

#da bot

worker = Worker.init()
logger = log_to_stderr()
logger.setLevel(logging.INFO)
m = multiprocessing.Manager()


@atexit.register
def cleanup():
    stoppool = threading.Thread(target=worker.close())
    stoppool.daemon = True
    stoppool.start()
    print"cleaning up.."
    print "bye!"





class DA_BOT(irc.IRCClient):
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


    @profiler.time_execution
    def parseCommand(self, usr, msg, chan):

        plgname = msg.split()[0].replace("!", "")
        plugins = Loader()
        for plugin in plugins.load():
            plg = plugins.get(plugin)

            if msg.startswith(("!" + plugin["name"])):
                args = msg.replace(("!" + plugin["name"]), "")
                A, B = multiprocessing.Pipe()

                response =  plg.do(args, pipe=B)
                print response
                self.msg(chan, response)
                A.close()

        pass


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

    nickname = property(_get_nickname)
    realname = property(_get_realname)
    username = property(_get_username)


class DA_BOT_FACTORY(protocol.ClientFactory):
    protocol = DA_BOT

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
    for name in networks.keys():
        factory = DA_BOT_FACTORY(name, networks[name])

        host = networks[name]['host']
        port = networks[name]['port']

        if networks[name]['ssl']:

            reactor.connectSSL(host, port, factory, ssl.ClientContextFactory())
        else:
            reactor.connectTCP(host, port, factory)

    reactor.run()
