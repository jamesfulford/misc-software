from schema import *

from sqlalchemy.orm import sessionmaker

#
# Start transactions
#
Connection = sessionmaker(bind=engine)
session = Connection()

server_environment = {
    "HOSTINGA": [
        "aleph",
        "bet"
    ],
    "HOSTINGB": [
        "alpha",
        "beta",
        "gamma"
    ]
}

for server, environments in server_environment.items():
    s = Server(name=server)
    session.add(s)
    session.add_all((Environment(name=e, server=s) for e in environments))

session.commit()

for env in session.query(Environment).join(Server).order_by(Server.name).all():
    print "{}/ {}".format(env.server.name, env.name)
