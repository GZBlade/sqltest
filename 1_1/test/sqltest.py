# -*- coding:utf-8 -*-

import mysql.connector
from data_acq.database import DataBase
from data_acq.modbus import ModbusRequest, ModbusResponseA, ModbusResponseD, ModbusSource
from data_acq.queryrequest import queryrequest, create_session

from data_acq.redismanager import RedisManager
class MysqlConnector:
    def __init__(self, user, password, database, host='localhost', port=3306):
        self.config = {
            'user' : user, 'password':password, 'database':database, 'host':host, 'port':port
        }
    def connect_test(self):
        try:
            conn = mysql.connector.connect(**self.config)
            cursor = conn.cursor()
            cursor.execute('show tables')
            values = cursor.fetchall()
            print(values)
        except mysql.connector.Error as e:
            print(e.msg)


firstsource = dict(
    dataName = 'speed', 			
    deviceAddress = '172.16.10.100',	
    dataUnit = 'rad/s',			   
    dataType = 'holding_register',			  
    dataLength = 2,		   
    dataAddress = 12291,		
    deviceName = 'plc_1200',	
    devicePort = 502,		  
    deviceUnit = 1,		   
    funCode = 3)
#生成用于测试的数据源列表
def generate_source(demo):
    sources_list = []
    for i in range(10):
        sources_list.append(dict(**demo))
    for num in range(10):
        sources_list[num]['dataAddress'] = num + demo['dataAddress']
        sources_list[num]['dataName'] = demo['dataName'] + str(num)
        
    return sources_list

db_remote = DataBase(db_name='plcdaq', user='root', passwd='root', db_host='192.168.239.120')
#生成数据源的测试数据，并提交数据库
def create_test():
    session1 = create_session(db_remote)
    data_sources = generate_source(firstsource)
    sqlsource_list = []
    for line in data_sources:
        sourceline = ModbusSource(**line)
        session1.add(sourceline)

    session1.commit()
#读取数据源，生成modbus请求列表
def create_request():
    request_list = []
    req_list = queryrequest(db_remote)
    for req in req_list:
        request_list.append(ModbusRequest(req))
    return request_list

redis_config = dict(
    write_host = '192.168.239.120',
    write_port = 6379,
    read_host = '192.168.239.120',
    read_port = 6380
)

def create_redis():
    redis_write = RedisManager(redis_config['write_host'], redis_config['write_port'])
    redis_read = RedisManager(redis_config['read_host'], redis_config['read_port'])
    all_keys = redis_write.connection.keys()
    return redis_write, redis_read

rw, rr = create_redis()