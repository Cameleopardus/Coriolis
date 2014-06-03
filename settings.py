NUM_THREADS = 4
identity = {
    'eof': {
        'nickname': 'bob',
        'realname': 'dat guy',
        'username': 'EE OH EFF',
        'nickserv_pw': None
    },
}
networks = {
#    'Freenode': {
#        'host': 'chat.eu.freenode.net',
#        'port': 7000,
#        'ssl': True,
#        'identity': identity['eof'],
#        'autojoin': (
#            '#goawayimeof',
#        )

#    },
#

          'Hardchatz': {

           'host': 'irc.hardchats.org',
           'port': 6667,
           'ssl': False,
          'identity': identity['eof'],
           'autojoin': (
               '#testingstuff',
           )
       },


}


