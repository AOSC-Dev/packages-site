#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import pickle
import sqlite3

SQLITE_FUNCTION = 31
MAX_ROW = 10000

def sql_auth(sqltype, arg1, arg2, dbname, source):
    if sqltype in (sqlite3.SQLITE_READ, sqlite3.SQLITE_SELECT, SQLITE_FUNCTION):
        return sqlite3.SQLITE_OK
    else:
        return sqlite3.SQLITE_DENY

result = {'rows': []}

urifn = os.path.normpath(sys.argv[1]).replace('?', '%3f').replace('#', '%23')

try:
    conn = sqlite3.connect('file:%s?mode=ro' % urifn, uri=True)
    try:
        conn.enable_load_extension(True)
        conn.execute("SELECT load_extension('./mod_vercomp.so')")
        conn.enable_load_extension(False)
    except sqlite3.Error:
        pass
    conn.set_authorizer(sql_auth)
    cur = conn.cursor()
    cur.execute(sys.stdin.read())
    if cur.description:
        result['header'] = tuple(x[0] for x in cur.description)
    for i, row in enumerate(cur, 1):
        result['rows'].append(tuple(row))
        if i >= MAX_ROW:
            result['error'] = 'only showing the first %d rows' % MAX_ROW
            break
    conn.close()
except (sqlite3.Error, sqlite3.Warning) as ex:
    result['error'] = str(ex)

pickle.dump(result, sys.stdout.buffer, pickle.HIGHEST_PROTOCOL)
