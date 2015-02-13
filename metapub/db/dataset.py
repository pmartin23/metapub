from __future__ import absolute_import

from ..config import ENABLE_MYSQL

if ENABLE_MYSQL:
    import MySQLdb as mdb
    import MySQLdb.cursors as cursors
    import PySQLPool
    from ..config import get_process_log
    log = get_process_log()

else:
    log = None

from .boolean import BooleanQueryExpression

SQLValues = BooleanQueryExpression(_and=",")

DEFAULT_HOST = 'localhost'
DEFAULT_USER = 'medgen'
DEFAULT_PASS = 'medgen'
DEFAULT_DATASET = 'medgen'

class SQLData(object):
    def __init__(self, *args, **kwargs):
        self._db_host = kwargs.get('db_host', DEFAULT_HOST)
        self._db_user = kwargs.get('db_user', DEFAULT_USER)
        self._db_pass = kwargs.get('db_pass', DEFAULT_PASS)
        self._db_name = kwargs.get('dataset', DEFAULT_DATASET)

    def connect(self):
        return PySQLPool.getNewConnection(username=self._db_user, 
                password=self._db_pass, host=self._db_host, db=self._db_name)

    def cursor(self, execute_sql=None):
        conn = self.connect()
        cursor = conn.cursor(cursors.DictCursor)

        if execute_sql is not None:
            cursor.execute(execute_sql)

        return [conn, cursor]

    def fetchall(self, select_sql):
        log.debug(select_sql)
        try:
            return self.execute(select_sql).record
        except mdb.Error, e:
            log.warn(e)
            return None
        except TypeError:
            # no results
            return None

    def fetchrow(self, select_sql):
        results = self.fetchall(select_sql)
        return results[0] if results else None

    def fetchID(self, select_sql, id_colname='ID'):
        try:
            return self.fetchrow(select_sql)[id_colname]
        except TypeError:
            return None

    def fetchall_where(self, select_sql, _value, _key=SQLValues.tic('?')):
        return self.fetchall(select_sql.replace(_key, _value))

    def results2set(self, select_sql, col='PMID'):
        pubmeds = set()
        for row in self.fetchall(select_sql):
            pubmeds.add(str(row[col]))
        return pubmeds

    def insert(self, sql_insert, sql_values, do_tic=True):
        """
        :param sql_insert: string statement like 'insert into hgvs_query(hgvs_text, .....)'
        :param sql_values: list of values
        """
        if do_tic:
            sql_values = SQLValues.tic(sql_values)

        return self.execute(sql_insert + " values " + SQLValues.AND(sql_values))

    def drop_table(self, tablename):
        return self.execute(" drop table if exists " + tablename)

    def truncate(self, tablename):
        return self.execute(" truncate " + tablename)

    def execute(self, sql):
        if IS_DEBUG_ENABLED:
            print 'SQL.execute ' + sql
            print '#######'
        query = PySQLPool.getNewQuery(self.connect())
        query.Query(sql)

        return query

    def ping(self):
        """
        Same effect as calling 'mysql> call mem'
        :returns::self.schema_info(()
        """
        try:
            return self.schema_info()

        except mdb.Error, e:
            log.error("DB connection is dead %d: %s" % (e.args[0], e.args[1]))
            return False

    def schema_info(self):
        header = ['schema', 'engine', 'table', 'rows', 'million', 'data length', 'MB', 'index']
        return {'header': header, 'tables': self.fetchall('call mem')}

    def PMID(self, query):
        """
        Query is usually a SQL select statement, returning a list of PMID rows
        handler is usually the underlying MySQL MedGen linked database
        """
        pubmeds = set()
        for row in self.fetchall(query):
            pubmeds.add(str(row['PMID']))
        return pubmeds

    def hgvs_text(self, query):
        """
        Query is usually a SQL select statement, returning a list of PMID rows
        handler is usually the underlying MySQL MedGen linked database
        """
        pubmeds = set()
        for row in self.fetchall(query):
            pubmeds.add(str(row['hgvs_text']))
        return pubmeds

