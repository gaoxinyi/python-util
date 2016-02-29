#-*-coding:utf-8-*-

import pymongo
import sys

reload(sys)
sys.setdefaultencoding('utf8')
orm = pymongo.Connection("1.2.3.4",1234).common_db.coll_sql

def search_sql(id,data=None,order_by=' order by ID desc'):
	sqlPlus = orm.find_one({'key':id})
	if data != None:
		for key in data.keys():
			value = str(data[key]).split(';')
			if len(value) == 5:
				sqlPlus['sql'] += " AND %s%s'%s' AND %s%s'%s'"%(key,value[0],value[1],key,value[2],value[3])
			else:
				if len(value) == 2:	op = value[1]
				else:	op = '='
				if op == '=' and (value[0] == '' or value[0] == None or value[0] == 'null'):	pass
				elif value[0] in ['is null','is not null']:	sqlPlus['sql'] += " AND %s %s"%(key,value[0])
				elif op in ['in','not in']:	sqlPlus['sql'] += " AND %s %s(%s)"%(key,op,value[0])
				else:	sqlPlus['sql'] += " AND %s%s'%s'"%(key,op,value[0])
		sqlPlus['sql'] += order_by
		# print sqlPlus['sql']
	return sqlPlus

def insert(conn,table,data=None):
	if data == None or data.keys() == 0:
		return False
	else:
		for key in data.keys():
			if data[key] == None or data[key] == '':	del data[key]
			else:   data[key] = str(data[key])
		cursor = conn.cursor()
		sql = "insert into %s(%s) values('%s')"%(table,",".join(data.keys()),"','".join(data.values()))
		print sql
		if cursor.execute(sql):
			cursor.close()
			conn.commit()
			return True
		else:
			cursor.close()
			conn.rollback()
			return False

def inserts(conn,table,data=[]):
	if len(data) == 0:
		return False
	else:
		cursor = conn.cursor()
		values = []
		keys = data[0].keys()
		len_keys = ('%s,'*len(keys))[:-1]
		for d in data:
			values.append(tuple(d.values()))
		sql = "insert into %s(%s) values(%s)"%(table,",".join(keys),len_keys)
		if cursor.executemany(sql,values):
			cursor.close()
			conn.commit()
			return True
		else:
			cursor.close()
			conn.rollback()
			return False

def update(conn,table,data=None,query=None):
	if data == None or data.keys() == 0:
		return False
	else:
		cursor = conn.cursor()
		sql = "update %s set "%(table)
		for key in data.keys():
			sql += "%s='%s',"%(key,data[key])
		sql = sql[0:-1]
		if query != None and query.keys() > 0:
			sql += " where 1=1"
			for q in query.keys():
				value = str(query[q]).split(';')
				if len(value) == 2:	op = value[1]
				elif value[0] in ['is null','is not null']:
					sql += " AND %s %s"%(q,value[0])
					continue
				else:	op = '='
				if op in ['in','not in']:	sql += " AND %s %s(%s)"%(q,op,value[0])
				else:	sql += " AND %s%s'%s'"%(q,op,value[0])
		# print sql
		cursor.execute(sql)
		cursor.close()
		conn.commit()
		return True

def save(conn,table,data=None,query=None):
	if searchOne(conn,'count.'+table,query)['COUNT'] == 0:
		insert(conn,'t_'+table,data)
	else:
		update(conn,'t_'+table,data,query)

def delSave(conn,table,data=[],page_no=1):
	if len(data) != 0:
		cursor = conn.cursor()
		if int(page_no) == 1:
			cursor.execute('truncate table ' + table)
			cursor.close()
		return inserts(conn,table,data)
	else:	return False

def decodeSQL(column,res):
	res_map = None
	if res != None:
		res_map = {}
		idx = 0
		for col in column.split(','):
			res_map[col.upper()] = res[idx]
			idx += 1
	return res_map

def searchOne(conn,id,data=None):
	cursor = conn.cursor()
	sqlPlus = search_sql(id,data)
	cursor.execute(sqlPlus['sql'])
	res = decodeSQL(sqlPlus['column'],cursor.fetchone())
	cursor.close()
	return res

def search(conn,id,data=None,order_by=' order by ID desc'):
	cursor = conn.cursor()
	sqlPlus = search_sql(id,data,order_by)
	cursor.execute(sqlPlus['sql'])
	res = []
	for item in cursor.fetchall():
		res.append(decodeSQL(sqlPlus['column'],item))
	cursor.close()
	return res

def searchPage(conn,id,data=None,page={'num':0,'size':20},order_by=' order by ID desc'):
	cursor = conn.cursor()
	sqlPlus = search_sql(id,data,order_by)
	cursor.execute('select COUNT(1) from'+sqlPlus['sql'].split('from')[1])
	count = cursor.fetchone()[0]
	res = []
	if count > 0:
		cursor.execute(sqlPlus['sql']+' limit %d,%d'%(page['num']*page['size'],page['size']))
		for item in cursor.fetchall():
			res.append(decodeSQL(sqlPlus['column'],item))
	cursor.close()
	return {'count':count,'res':res}

def searchSelf(conn,id,data=None):
	cursor = conn.cursor()
	sqlPlus = search_sql(id,data)
	sql = sqlPlus['sql'].split('@')
	cursor.execute(sql[0].replace('#',sql[1][0:-16]))
	res = []
	for item in cursor.fetchall():
		res.append(decodeSQL(sqlPlus['column'],item))
	cursor.close()
	return res
