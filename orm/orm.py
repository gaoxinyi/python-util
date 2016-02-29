#-*-coding:utf-8-*-

# 引入mongodb的封装类
import pymongo
import sys

# 设置字符编码为utf8
reload(sys)
sys.setdefaultencoding('utf8')
# 连接mongodb数据库  1.2.3.4为ip。1234为端口。可以根据数据库的情况自定义。common_db是数据库名称。coll_sql为表名
orm = pymongo.Connection("1.2.3.4",1234).common_db.coll_sql

# 生成查询sql id->mdb数据库中的key。用来指定对应的查询语句 data->查询条件 order_by->默认是根据ID倒序。可以自定义排序方式。
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

# 插入数据库 conn->连接对象 table->表名 data->插入数据
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

# 插入数据(批量) conn->连接对象 table->表名 data->插入数据(列表)
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

# 修改数据 conn->连接对象 table->表名 data->修改信息 query->查询条件
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

# 修改或插入(如果数据不存在则插入反之则修改) conn->连接对象 table->表名 data->修改信息 query->查询条件
def save(conn,table,data=None,query=None):
	if searchOne(conn,'count.'+table,query)['COUNT'] == 0:
		insert(conn,'t_'+table,data)
	else:
		update(conn,'t_'+table,data,query)

# 对结果集进行映射。column->映射的字段名 res->结果集
def decodeSQL(column,res):
	res_map = None
	if res != None:
		res_map = {}
		idx = 0
		for col in column.split(','):
			res_map[col.upper()] = res[idx]
			idx += 1
	return res_map

# 查询满足条件的一条记录如果没有满足条件返回None
# conn->连接对象 id->mdb数据库中的key。用来指定对应的查询语句 data->查询条件
def searchOne(conn,id,data=None):
	cursor = conn.cursor()
	sqlPlus = search_sql(id,data)
	cursor.execute(sqlPlus['sql'])
	res = decodeSQL(sqlPlus['column'],cursor.fetchone())
	cursor.close()
	return res

# 查询所有满足条件的记录如果没有满足条件返回None
# conn->连接对象 id->mdb数据库中的key。用来指定对应的查询语句 data->查询条件 order_by->默认是根据ID倒序。可以自定义排序方式。
def search(conn,id,data=None,order_by=' order by ID desc'):
	cursor = conn.cursor()
	sqlPlus = search_sql(id,data,order_by)
	cursor.execute(sqlPlus['sql'])
	res = []
	for item in cursor.fetchall():
		res.append(decodeSQL(sqlPlus['column'],item))
	cursor.close()
	return res

# 查询所有满足当前分页条件的记录
# conn->连接对象 id->mdb数据库中的key。用来指定对应的查询语句 data->查询条件 page->默认一页20条 order_by->默认是根据ID倒序。可以自定义排序方式。
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
# 高级查询。具体参照Demo
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
