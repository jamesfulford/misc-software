from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

from sqlalchemy.orm import sessionmaker

#
# Following sqlalchemy tutorial
#

engine = create_engine('sqlite:///:memory:', echo=False)
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    password = Column(String)

    def __repr__(self):
        return "<User(name='%s', fullname='%s', password='%s')>" % (
            self.name,
            self.fullname,
            self.password
        )


Base.metadata.create_all(engine)

#
# Start transactions
#
Session = sessionmaker(bind=engine)
session = Session()

ed_user = User(name='ed', fullname='Ed Jones', password='edspassword')

session.add(ed_user)
session.commit()
print ed_user.name, ed_user.password, ed_user.fullname, str(ed_user.id)

ed_user.password = "abcd"
session.commit()
print ed_user.name, ed_user.password, ed_user.fullname, str(ed_user.id)

print session.query(User).all()
