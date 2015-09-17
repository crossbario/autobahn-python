from autobahn.twisted.wamp import Connection

def on_join(session):
    print('session connected: {}'.format(session))
    session.leave()

def main(connection):
    connection.on_join(on_join)

if __name__ == '__main__':
    from twisted.internet import reactor

    #connection = Connection()
    #done = connection.connect(main)

    def finish(res):
        print(res)
        #reactor.stop()

    #done.addBoth(finish)

    reactor.run()
