import psycopg2
from psycopg2.extras import RealDictCursor


class RedShiftWrapper():
    def __init__(self, _dbname, _host, _user, _pwd, _port):
        self.dbname = _dbname
        self.host = _host
        self.user = _user
        self.pwd = _pwd
        self.port = _port

    @staticmethod
    def query_with_sql(sql, self, data=None):
        with psycopg2.connect(dbname=self['dbname'], user=self['user'], password=self['pwd'],
                              host=self['host'], port=self['port']) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(sql, data)
                return cursor.fetchall()
