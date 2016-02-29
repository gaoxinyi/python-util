# #-*-coding:utf-8-*-

"""
	mongodb 数据
	{u'column': u'ID,ORDER_CODE,CONSIGNEE_CONTACT,CONSIGNEE_PHONE_NO,CONSIGNEE_PROVINCE,CONSIGNEE_CITY,CONSIGNEE_COUNTY,
	CONSIGNEE_ADDRESS,SHIPPING_STATUS,SHIPPING_NOTE_NO,SHIPPING_DATE,TOTAL_WEIGHT,SYNC,EXPRESS_CODE,CONSIGNEE_TYPE,AREACODE,
	ITEM_QTY,CREATE_DATE,NET_WEIGHT,BEFORE_STATUS,CONSIGNEE_TEL,SHOP_NAME', u'_id': u'14351151798563783', 
	u'key': u'maji.search.order', u'sql': u"select ID,ORDER_CODE,CONSIGNEE_CONTACT,CONSIGNEE_PHONE_NO,CONSIGNEE_PROVINCE,
	CONSIGNEE_CITY,CONSIGNEE_COUNTY,CONSIGNEE_ADDRESS,SHIPPING_STATUS,SHIPPING_NOTE_NO,date_format(SHIPPING_DATE,'%Y-%m-%d %T'),
	TOTAL_WEIGHT,SYNC,EXPRESS_CODE,CONSIGNEE_TYPE,AREACODE,ITEM_QTY,date_format(CREATE_DATE,'%Y-%m-%d %T'),NET_WEIGHT,BEFORE_STATUS,
	CONSIGNEE_TEL,SHOP_NAME from t_order WHERE 1=1"}

	column->返回结果按照顺序映射的字段名。
	sql->查询语句。最后加的WHERE 1=1 是因为查询条件是动态的。框架会把查询条件拼接到后面如 AND ORDER_CODE='test'
	key->这条查询语句对应的key。用来在调用的时候传递。

	mysql 表结构
	CREATE TABLE `t_order` (
	  `ID` int(11) NOT NULL,
	  `CONSIGNOR_CODE` varchar(45) NOT NULL DEFAULT 'maji',
	  `ORDER_CODE` varchar(45) NOT NULL,
	  `EXPRESS_CODE` varchar(10) NOT NULL,
	  `CONSIGNEE_TYPE` varchar(1) DEFAULT NULL,
	  `CONSIGNEE_CONTACT` varchar(45) NOT NULL,
	  `CONSIGNEE_TEL` varchar(20) DEFAULT NULL,
	  `CONSIGNEE_PHONE_NO` varchar(20) DEFAULT NULL,
	  `CONSIGNEE_PROVINCE` varchar(45) NOT NULL,
	  `CONSIGNEE_CITY` varchar(45) NOT NULL,
	  `CONSIGNEE_COUNTY` varchar(45) NOT NULL,
	  `CONSIGNEE_ADDRESS` varchar(200) NOT NULL,
	  `SHIPPING_STATUS` varchar(5) DEFAULT '0',
	  `SHIPPING_NOTE_NO` varchar(45) DEFAULT NULL,
	  `SHIPPING_DATE` timestamp NULL DEFAULT NULL,
	  `TOTAL_WEIGHT` float DEFAULT NULL,
	  `SYNC` int(1) DEFAULT '0',
	  `CREATE_DATE` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
	  `AREACODE` varchar(200) DEFAULT NULL,
	  `ITEM_QTY` int(6) DEFAULT NULL,
	  `MODIFY_DATE` timestamp NULL DEFAULT NULL,
	  `BEFORE_STATUS` varchar(5) DEFAULT NULL,
	  `NET_WEIGHT` float DEFAULT NULL,
	  `SHOP_NAME` varchar(32) DEFAULT NULL,
	  PRIMARY KEY (`ID`),
	  UNIQUE KEY `uq_order_code` (`ORDER_CODE`)
	) ENGINE=InnoDB DEFAULT CHARSET=utf8;
"""

import orm
import MySQLdb

conn = MySQLdb.connect(host="1.2.3.4",user="test",passwd="test",db="db_test",charset="utf8")

"""
	查询条件写法
	1.等值		{"COLUMN":"VALUE"}
	2.不等		{"COLUMN":"VALUE;!="}
	3.范围(单向)	{"COLUMN":"VALUE;>"}
	4.范围(双向)	{"COLUMN":">=;VALUE1;<=;VALUE2"}
	5.不为空		{"COLUMN":"is not null"}
	6.为空		{"COLUMN":"is null"}
	7.in 		{"COLUMN":"VALUE1,VALUE2,VALUE3;in"}
	8.not in 	{"COLUMN":"VALUE1,VALUE2,VALUE3;not in"}
"""
# 查询一条记录
orm.searchOne(conn,"maji.search.order",{"ORDER_CODE":"test"})
# 返回结果为{"ORDER_CODE":"test",...}

# 查询所有记录
orm.search(conn,"maji.search.order",{"SHIPPING_STATUS":"1"})
# 返回结果为[{"ORDER_CODE":"test","SHIPPING_STATUS":"1",...},{"ORDER_CODE":"test2","SHIPPING_STATUS":"1",...}]

# 分页查询
orm.searchPage(conn,"maji.search.order",{"SHIPPING_STATUS":"1"},{"num":0,"size":100})
# 返回结果为{"count":1000,res:[{"ORDER_CODE":"test","SHIPPING_STATUS":"1",...},{"ORDER_CODE":"test2","SHIPPING_STATUS":"1",...}]}