from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship


engine = create_engine('sqlite:///:memory:', echo=False)
Base = declarative_base()


class Server(Base):
    __tablename__ = 'server'
    id = Column(Integer, primary_key=True)
    name = Column(String)

    ip = Column(String)
    url = Column(String)

    environments = relationship('Environment', back_populates='server')

    def __str__(self):
        return "https://{url}/{name}".format(
            url=self.url if self.url else self.ip,
            name=self.name
        )


class Environment(Base):
    __tablename__ = 'environment'
    id = Column(Integer, primary_key=True)
    name = Column(String)

    # always the max value in Report
    version = Column(String)

    server_id = Column(Integer, ForeignKey('server.id'))
    server = relationship("Server", back_populates="environments")

    reports = relationship("Report", back_populates="environment")


class Report(Base):
    __tablename__ = "report"
    id = Column(Integer, primary_key=True)

    source_version = Column(String)
    target_version = Column(String)

    email_address = Column(String)

    # source environment
    environment_id = Column(Integer, ForeignKey("environment.id"))
    environment = relationship("Environment", back_populates="reports")


Base.metadata.create_all(engine)
