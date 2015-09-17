from autobahn.twisted import run


def on_join(session):
    print('session connected: {}'.format(session))
    session.leave()


def main(connection):
    connection.session.on_join(on_join)


if __name__ == '__main__':
    return run(main)
