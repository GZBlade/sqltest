# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""Module docstring.

modbus info
"""

__author__ = 'WangNima'

import struct
import time

import modbus_tk
import modbus_tk.defines as cst
from sqlalchemy import Column, String, Integer, Float
from sqlalchemy.ext.declarative import declarative_base


class ModbusRequest(object):
    def __init__(self, requestvar):
        self.data_name = requestvar[1]
        self.dev_addr = requestvar[2] #modbus server IP_address
        self.data_unit = requestvar[3]
        self.data_type = requestvar[4]
        self.data_length = requestvar[5] #quality_of_x
        self.data_addr = requestvar[6] #start_addr
        self.dev_name = requestvar[7]
        self.dev_port = requestvar[8]
        self.dev_unit = requestvar[9] #slaveID
        self.fun_code = requestvar[10] #funcode

Base = declarative_base()

class ModbusSource(Base):
    def __init__(self,dataName,deviceAddress,dataUnit,dataType,dataLength,dataAddress,deviceName,devicePort,deviceUnit,funCode):
        self.dataName = dataName
        self.deviceAddress = deviceAddress
        self.dataUnit = dataUnit
        self.dataType = dataType
        self.dataLength = dataLength
        self.dataAddress = dataAddress
        self.deviceName = deviceName
        self.devicePort = devicePort
        self.deviceUnit = deviceUnit
        self.funCode = funCode

    __tablename__ = 'datasources'
    id = Column(Integer, primary_key=True, autoincrement=True)
    dataName = Column(String(50))   
    deviceAddress = Column(String(50))
    dataUnit = Column(String(50))
    dataType = Column(String(50))
    dataLenght = Column(Integer)
    dataAddress = Column(Integer)
    deviceName = Column(String(50))
    devicePort = Column(Integer)
    deviceUnit = Column(Integer)
    funCode = Column(Integer)

class ModbusResponseA(Base):
    def __init__(self, modbusreq, data):
        self.DataName = modbusreq.data_name
        self.DataType = modbusreq.data_type
        self.DataUnit = modbusreq.data_unit
        self.Timestamp = time.strftime('%Y-%m-%d %X', time.localtime())
        self.DataAddress = modbusreq.data_addr
        self.DeviceName = modbusreq.dev_name
        self.DeviceAddress = modbusreq.dev_addr
        self.DevicePort = modbusreq.dev_port
        self.DeviceUnit = modbusreq.dev_unit
        self.DataValue = data
        self.FunCode = modbusreq.fun_code
        self.DataLenth = modbusreq.data_length
    def get_modbusresponseA(self):
        modbus_responseA = self.__dict__
        data_key = self.Timestamp + ':' + self.DataName + ':' + self.DeviceAddress
        return [data_key,modbus_responseA]
    __tablename__ = 'historydataA'
    id = Column(Integer, primary_key=True, autoincrement=True)
    DataName = Column(String(50))
    DeviceAddress = Column(String(50))
    Timestamp = Column(String(50))
    DataValue = Column(Float)
    DataUnit = Column(String(50))
    DataType = Column(String(50))
    DataLenth = Column(Integer)
    DataAddress = Column(Integer)
    DeviceName = Column(String(50))
    DevicePort = Column(Integer)
    DeviceUnit = Column(Integer)
    FunCode = Column(Integer)


class ModbusResponseD(Base):
    def __init__(self, modbusreq, data):
        self.DataName = modbusreq.data_name
        self.DataType = modbusreq.data_type
        self.Timestamp = time.strftime('%Y-%m-%d %X', time.localtime())
        self.DataAddress = modbusreq.data_addr
        self.DeviceName = modbusreq.dev_name
        self.DeviceAddress = modbusreq.dev_addr
        self.DevicePort = modbusreq.dev_port
        self.DeviceUnit = modbusreq.dev_unit
        self.DataValue = data
        self.FunCode = modbusreq.fun_code
        self.DataLenth = modbusreq.data_length

    __tablename__ = 'historydataD'
    id = Column(Integer, primary_key=True, autoincrement=True)
    DataName = Column(String(50))
    DeviceAddress = Column(String(50))
    Timestamp = Column(String(50))
    DataValue = Column(Integer)
    DataType = Column(String(50))
    DataLenth = Column(Integer)
    DataAddress = Column(Integer)
    DeviceName = Column(String(50))
    DevicePort = Column(Integer)
    DeviceUnit = Column(Integer)
    FunCode = Column(Integer)

funcode = {1: cst.READ_COILS, 2: cst.READ_DISCRETE_INPUTS,
           3: cst.READ_HOLDING_REGISTERS, 4: cst.READ_INPUT_REGISTERS}

def send_modbus(modbus_req, master):
    logger = modbus_tk.utils.create_logger("console")
    try:
        #logger.info("connected")

        response = master.execute(modbus_req.dev_unit,
                                  funcode[modbus_req.fun_code],
                                  modbus_req.data_addr,
                                  modbus_req.data_length)
        print(response)
        if modbus_req.fun_code == 3 or modbus_req.fun_code == 4:
            data_value = bytes16ToFloat(response[0], response[1])
            print(data_value)
            return data_value
        else:
            print(response[0])
            return response[0]

    except modbus_tk.modbus.ModbusError as e:
        logger.error("%s- Code=%d" % (e, e.get_exception_code()))
        raise


def bytes16ToFloat(h1, h2):
    return bytesToFloat((h1 & 0xFF00) >> 8, h1 & 0xFF, (h2 & 0xFF00) >> 8, h2 & 0xFF)


def bytesToFloat(h1, h2, h3, h4):
    ba = bytearray()
    ba.append(h1)
    ba.append(h2)
    ba.append(h3)
    ba.append(h4)
    return struct.unpack("!f", ba)[0]