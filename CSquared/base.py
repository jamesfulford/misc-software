from css.release import utilities as u
from css.release.query.datastream import DataStream


class QueryStream(DataStream):
    def __init__(self):
        super(QueryStream, self).__init__()

    @property
    def query_arguments(self):
        """
        Returns all needed arguments for a query
        """
        return {}

    def input(self):
        """
        Returns list of records to either to enter into the query stream
        """
        sql = self.sql

        query_arguments = {}
        if hasattr(self, "query_arguments"):
            query_arguments = self.query_arguments

        return u.run_query(sql, **query_arguments)
