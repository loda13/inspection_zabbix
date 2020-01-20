# inspection_zabbix
based on zabbix-database


使用修改项：

1、# zabbix数据库信息

zdbhost = 'x.x.x.x'
zdbuser = 'xxxx'
zdbpass = 'xxxx'
zdbport = 'xxxx'
zdbname = 'xxxx'

2、指标修改
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
    
    3、报告导出路径
    workbook = xlsxwriter.Workbook('/xxx/xxx/xxx/%s_%s巡检报告.xlsx' % (date_from, date_to))
    
    4、列名和取值
    
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
            
            
            
   ps:
   欢迎使用。
