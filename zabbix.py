#!/usr/local/python/bin/python3.5
import datetime
import smtplib
import time
from email.header import Header
from email.mime.text import MIMEText

import xlsxwriter
import pymysql

# zabbix数据库信息

zdbhost = 'x.x.x.x'
zdbuser = 'xxxx'
zdbpass = 'xxxxxx'
zdbport = xxxx
zdbname = 'xxxx'

d = datetime.datetime.now()
day = datetime.date.today()
keys = {
    'trends_uint': [
        'net.if.in[eth0]',
        'net.if.out[eth0]',
        'vm.memory.size[available]',
        'system.uptime',
    ],
    'trends': [
        'system.cpu.load[percpu,avg5]',
        'system.cpu.util[,idle]',
        'vfs.fs.size[/,pfree]',
        'vfs.fs.size[/home,pfree]',
        'vfs.fs.size[/disk1,pfree]',
        'cpu_utilization',
        'mem_used',
        'system.swap.size[,pfree]',
    ],
}


def getinfo():
    for ip, resultdict in zabbix.IpInfoList.items():
        print("正在查询 IP:%-15s hostid:%5d 的信息！" % (ip, resultdict['hostid']))
        for table, keylists in keys.items():
            for key in keylists:
                print("\t正在统计 key_:%s" % key)
                data = zabbix.getLastMonthData(resultdict['hostid'], table, key)
                zabbix.IpInfoList[ip][key] = data


class ReportForm:

    def __init__(self):
        self.conn = pymysql.connect(host=zdbhost, user=zdbuser, passwd=zdbpass, port=zdbport, db=zdbname)
        self.cursor = self.conn.cursor()
        self.groupname = 'xxxx'
        self.IpInfoList = self.__getHostList()
        # return self.IpInfoList

    def __getHostList(self):
        sql = '''select groupid from groups where name = '%s' ''' % self.groupname
        self.cursor.execute(sql)
        groupid = self.cursor.fetchone()[0]
        print(groupid)

        sql = '''select hostid from hosts_groups where groupid = %s''' % groupid
        self.cursor.execute(sql)
        hostlist = self.cursor.fetchall()

        IpInfoList = {}
        for i in hostlist:
            hostid = i[0]
            sql = '''select host from hosts where status = 0 and hostid = %s''' % hostid
            ret = self.cursor.execute(sql)
            if ret:
                IpInfoList[self.cursor.fetchone()[0]] = {'hostid': hostid}
        return IpInfoList

    def __getItemid(self, hostid, itemname):
        sql = '''select itemid from items where hostid = %s and key_ = '%s' ''' % (hostid, itemname)
        if self.cursor.execute(sql):
            itemid = self.cursor.fetchone()[0]
        else:
            itemid = 1
        return itemid

    def getTrendsValue(self, itemid, start_time, stop_time):
        resultlist = {}
        for type in ['min', 'max', 'avg']:
            sql = '''select %s(value_%s) as result from trends where itemid = %s
            and clock >= %s and clock <= %s''' % (type, type, itemid, start_time, stop_time)
            self.cursor.execute(sql)
            result = self.cursor.fetchone()[0]
            if result == None:
                result = 0
            resultlist[type] = result
        return resultlist

    def getTrends_uintValue(self, itemid, start_time, stop_time):
        resultlist = {}
        for type in ['min', 'max', 'avg']:
            sql = '''select %s(value_%s) as result from trends_uint where itemid = %s
            and clock >= %s and clock <= %s''' % (type, type, itemid, start_time, stop_time)
            self.cursor.execute(sql)
            result = self.cursor.fetchone()[0]
            if result:
                resultlist[type] = int(result)
            else:
                resultlist[type] = 0
        return resultlist

    def get_week(self, d):
        dayscount = datetime.timedelta(days=d.isoweekday())
        dayto = d - dayscount
        sixdays = datetime.timedelta(days=6)
        dayfrom = dayto - sixdays
        date_from = datetime.datetime(dayfrom.year, dayfrom.month, dayfrom.day, 0, 0, 0)
        date_to = datetime.datetime(dayto.year, dayto.month, dayto.day, 23, 59, 59)
        ts_first = int(time.mktime(datetime.datetime(dayfrom.year, dayfrom.month, dayfrom.day, 0, 0, 0).timetuple()))
        ts_last = int(time.mktime(datetime.datetime(dayto.year, dayto.month, dayto.day, 23, 59, 59).timetuple()))
        return ts_first, ts_last

    def getLastMonthData(self, hostid, table, itemname):
        ts_first = self.get_week(d)[0]
        ts_last = self.get_week(d)[1]
        itemid = self.__getItemid(hostid, itemname)
        # function = getattr(self, 'get %s Value' % table.capitalize())
        function = getattr(self, 'get%sValue' % table.capitalize())
        return function(itemid, ts_first, ts_last)

    def writeToXls(self):
        dayscount = datetime.timedelta(days=d.isoweekday())
        dayto = d - dayscount
        sixdays = datetime.timedelta(days=6)
        dayfrom = dayto - sixdays
        date_from = datetime.date(dayfrom.year, dayfrom.month, dayfrom.day)
        date_to = datetime.date(dayto.year, dayto.month, dayto.day)
        '''生成xls文件'''
        try:
            import xlsxwriter
            # 创建文件
            workbook = xlsxwriter.Workbook('/xxx/xxx/xxx/%s_%s巡检报告.xlsx' % (date_from, date_to))
            # 创建工作薄
            worksheet = workbook.add_worksheet()
            # 写入标题（第一行）
            i = 0
            #for value in ["主机", "CPU平均空闲值", "CPU最小空闲值", "可用平均内存(单位M)", "可用最小内存(单位M)", "CPU5分钟负载", "/磁盘%"]:
            for value in ["主机ip", "CPU使用率%", "CPU5分钟负载", "内存使用率%", "/磁盘使用率%", "/disk1使用率%", "uptime/天", "swap分区使用率%"]:

                worksheet.write(0, i, value)
                i = i + 1
            # 写入内容：
            j = 1
            for ip, value in self.IpInfoList.items():
                worksheet.write(j, 0, ip)
                worksheet.write(j, 1, '%.2f' % value['cpu_utilization']['avg'])
                # worksheet.write(j, 2, '%.2f' % value['system.cpu.util[,idle]']['min'])
                # worksheet.write(j, 3, '%dM' % int(value['vm.memory.size[available]']['avg'] / 1024 / 1024))
                # worksheet.write(j, 4, '%dM' % int(value['vm.memory.size[available]']['min'] / 1024 / 1024))
                worksheet.write(j, 2, '%.2f' % value['system.cpu.load[percpu,avg5]']['avg'])
                worksheet.write(j, 3, '%.2f' % value['mem_used']['avg'])
                worksheet.write(j, 4, 100.00 - float('%.2f' % value['vfs.fs.size[/,pfree]']['avg']))
                worksheet.write(j, 5, 100.00 - float('%.2f' % value['vfs.fs.size[/disk1,pfree]']['avg']))
                # worksheet.write(j, 7, '%.2f' % value['vfs.fs.size[/home,pfree]']['avg'])
                worksheet.write(j, 6, value['system.uptime']['avg'] / 60 / 60 / 24)
                worksheet.write(j, 7, 100.00 - float('%.2f' % value['system.swap.size[,pfree]']['avg']))
                j = j + 1
            workbook.close()
        except Exception as e:
            print(e)

    def __del__(self):
        """关闭数据库连接"""
        self.cursor.close()
        self.conn.close()


if __name__ == "__main__":
    zabbix = ReportForm()
    getinfo()
    zabbix.writeToXls()
