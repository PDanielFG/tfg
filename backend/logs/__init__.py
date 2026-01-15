import sys
if sys.platform == "win32":
    import pymysql
    pymysql.install_as_MySQLdb()
