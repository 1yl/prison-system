# coding:utf-8
import psycopg2
import time, os, re, datetime, json
from functools import reduce
from decorate import cur_p


class  FlaskAPI():
    # TODO：关闭数据库
    @staticmethod
    def close_database(conn, cur):
        conn.commit()
        cur.close()
        conn.close()

    # TODO：将字典数据转换为字符串的形式
    @staticmethod
    def deal_data(data):
        if type(data) == list and len(data) > 0:
            key = [i for i in data[0].keys()]
            key = '(' + ','.join(key) + ')'
            value = ','.join([str(list(i.values())).replace(']', ')').replace('[', '(') for i in data])
            return key, value
        else:
            return 'error'

    # TODO：插入数据
    @staticmethod
    @cur_p
    def write(data, table, cur='', conn=''):
        res1 = FlaskAPI.deal_data(data)
        if res1 == 'error':
            return res1
        else:
            try:
                cur.execute("insert into {0} {1} values{2};".format(table, res1[0], res1[1]))
                return 'success'
            except psycopg2.Error as e:
                print('错误原因：', e)
                return 'error'

    # TODO：读取数据，并将日期进行格式化
    @staticmethod
    @cur_p
    def read(table, target_field='', condition='', cur='', conn=''):
        try:
            if target_field:
                target_field = ','.join(target_field)
            else:
                target_field = '*'
            if condition:
                cur.execute("select {0} from {1} where {2}; ".format(target_field, table, condition))
                # print("select {0} from {1} where {2}; ".format(target_field, table, condition))
                res = cur.fetchall()
                # print(res)
                if res:
                    # print(123)
                    for i in res:
                        if 'message_last_post' in res[0].keys():
                            if i['message_last_post'] is not None:
                                i['message_last_post'] = i['message_last_post'].__format__('%Y-%m-%d %H:%M:%S')
                            else:
                                i['message_last_post'] = ''
                        if 'create_date' in res[0].keys():
                            if i['create_date'] is not None:
                                i['create_date'] = i['create_date'].__format__('%Y-%m-%d %H:%M:%S')
                            else:
                                i['create_date'] = ''
                        if 'write_date' in res[0].keys():
                            if i['write_date'] is not None:
                                i['write_date'] = i['write_date'].__format__('%Y-%m-%d %H:%M:%S')
                            else:
                                i['write_date'] = ''
                return res
            else:
                cur.execute("select {0} from {1} ; ".format(target_field, table))
                res = cur.fetchall()
                if res:
                    for i in res:
                        if 'message_last_post' in res[0].keys():
                            if i['message_last_post'] is not None:
                                i['message_last_post'] = i['message_last_post'].__format__('%Y-%m-%d %H:%M:%S')
                            else:
                                i['message_last_post'] = ''
                        if 'create_date' in res[0].keys():
                            if i['create_date'] is not None:
                                i['create_date'] = i['create_date'].__format__('%Y-%m-%d %H:%M:%S')
                            else:
                                i['create_date'] = ''
                        if 'write_date' in res[0].keys():
                            if i['write_date'] is not None:
                                i['write_date'] = i['write_date'].__format__('%Y-%m-%d %H:%M:%S')
                            else:
                                i['write_date'] = ''
                return res
        except psycopg2.Error:
            return 'error'

    # TODO：将数据库表中数据打包，命名方式以当前时间的年月日时进行命名
    @staticmethod
    @cur_p
    def clear_sql(table, sign, cur='', conn=''):
        # res=cls.cur()
        if sign != 1:
            now_time = time.localtime(time.time())
            file_name = str(now_time.tm_year) + '-' + str(now_time.tm_mon) + '-' + str(now_time.tm_mday) + '-' + str(
                now_time.tm_hour)
            print(file_name)
            print('开始执行')
            cur.execute('select * from {0};'.format(table))
            cur.fetchall()
            # cur.execute("COPY (select * from {0}) to '/Users/mac/Desktop/data/{1}.csv' with csv header;".format(table, file_name))
            cur.execute("COPY (select * from {0}) to '/root/flask_data/{1}.csv' with csv header;".format(table, file_name))
                # "COPY (select * from {0}) to '/flask_data/{1}.csv' with csv header;".format(table, file_name))
            cur.execute('TRUNCATE TABLE {0} RESTART IDENTITY CASCADE;'.format(table))
            print('执行结束')
            # return dic_lis

    # TODO：将state_table表中符合查询条件的设备信息返回
    @staticmethod
    @cur_p
    def search_psql(start_time, end_time, device_id, cur='', conn=''):
        if start_time and end_time:
            start_time = time.strptime(start_time, '%Y-%m-%d %H:%M:%S')
            start_time = time.mktime(start_time)
            end_time = time.strptime(end_time, '%Y-%m-%d %H:%M:%S')
            end_time = time.mktime(end_time)
            print("111", start_time)
            print("222", end_time)
            print("333", device_id)
            try:
                cur.execute(
                    "select * from state_table where time >={0} and time <={1} and name='{2}';".format(
                        start_time, end_time, device_id))
                data = cur.fetchall()
                return data
            except:
                return 'error'
        else:
            return ''

    # TODO：将fresh_table表中符合查询条件的设备信息返回
    @staticmethod
    @cur_p
    def search_fsql(start_time, end_time, device_id, cur='', conn=''):
        if start_time and end_time:
            start_time = time.strptime(start_time, '%Y-%m-%d %H:%M:%S')
            start_time = time.mktime(start_time)
            end_time = time.strptime(end_time, '%Y-%m-%d %H:%M:%S')
            end_time = time.mktime(end_time)
            print("111", start_time)
            print("222", end_time)
            print("333", device_id)
            try:
                cur.execute(
                    "select * from fresh_table where time >={0} and time <={1} and name='{2}';".format(
                        start_time, end_time, device_id))
                data = cur.fetchall()
                return data
            except:
                return 'error'
        else:
            return ''

    # TODO：根据fresh_table表中设备id查人员信息
    @staticmethod
    @cur_p
    def query_name(data, cur='', conn=''):
        try:
            cur.execute(
                "select name from prison_work_person where card_number='{0}';".format(data))
            data = cur.fetchall()
            return data
        except:
            return 'error'

    # TODO：将car_table表中符合查询条件的设备信息返回
    @staticmethod
    @cur_p
    def search_csql(start_time, end_time, device_id, cur='', conn=''):
        if start_time and end_time:
            start_time = time.strptime(start_time, '%Y-%m-%d %H:%M:%S')
            start_time = time.mktime(start_time)
            end_time = time.strptime(end_time, '%Y-%m-%d %H:%M:%S')
            end_time = time.mktime(end_time)
            print("111", start_time)
            print("222", end_time)
            print("333", device_id)
            try:
                cur.execute(
                    "select * from car_table where time >={0} and time <={1} and name='{2}';".format(
                        start_time, end_time, device_id))
                data = cur.fetchall()
                return data
            except:
                return 'error'
        else:
            return ''


    # TODO：将historical_alarm表中符合查询条件的设备信息返回
    @staticmethod
    @cur_p
    def search_hsql(start_time, end_time, device_id, cur='', conn=''):
        if start_time and end_time:
            start_time = time.strptime(start_time, '%Y-%m-%d %H:%M:%S')
            start_time = time.mktime(start_time)
            end_time = time.strptime(end_time, '%Y-%m-%d %H:%M:%S')
            end_time = time.mktime(end_time)
            print("111", start_time)
            print("222", end_time)
            print("333", device_id)
            try:
                cur.execute(
                    "select * from historical_alarm where time >={0} and time <={1} and name='{2}';".format(
                        start_time, end_time, device_id))
                data = cur.fetchall()
                return data
            except:
                return 'error'
        else:
            return ''

    # TODO: 报警信息插入
    @staticmethod
    @cur_p
    def bstate_data_insert(data, cur='', conn=''):
        try:
            res = FlaskAPI.deal_data(data)
            if res == 'error':
                return res
            else:
                try:
                    cur.execute("insert into historical_alarm {0} values {1};".format(res[0], res[1]))
                    return 'success'
                except psycopg2.Error as e:
                    print('错误原因：', e)
                    return 'error'
        except psycopg2.Error:
            return ''

    # TODO: 报警信息插入
    @staticmethod
    @cur_p
    def bstate_car_insert(data, cur='', conn=''):
        try:
            res = FlaskAPI.deal_data(data)
            if res == 'error':
                return res
            else:
                try:
                    cur.execute("insert into car_table {0} values {1};".format(res[0], res[1]))
                    return 'success'
                except psycopg2.Error as e:
                    print('错误原因：', e)
                    return 'error'
        except psycopg2.Error:
            return ''

    @staticmethod
    @cur_p
    def search_sql(start_time, end_time, device_id, cur='', conn=''):
        # lis = os.listdir('/flask_data')
        lis = os.listdir('/root/flask_data')
        data = '空'
        try:
            new_lis = list(map(lambda x: re.findall(r"(.+?)\.", x)[0], lis[1:]))
            # print(1, new_lis)
            if new_lis and start_time and end_time:
                data_lis = list(map(lambda x: x.split('-'), new_lis))
                # print(2, data_lis)
                date_lis = [int(x[0]) * 10 ** 6 + int(x[1]) * 10 ** 4 + int(x[2]) * 10 ** 2 + int(x[3]) for x in list(data_lis)]
                # print(3, date_lis)
                begin_time = re.findall(r'(.+?):', start_time)[0].replace(" ", "-")
                # print(4, begin_time)
                tim1 = begin_time.split('-')
                tim1 = int(tim1[0]) * 10 ** 6 + int(tim1[1]) * 10 ** 4 + int(tim1[2]) * 10 ** 2 + int(tim1[3])
                tim4 = time.strptime(end_time, '%Y-%m-%d %H:%M:%S')
                # print(5, tim4)
                tim4 = time.mktime(tim4) + 3600
                tim4 = time.localtime(tim4)
                tim4 = time.strftime("%Y-%m-%d-%H", tim4)
                # print(6, tim4)
                tim2 = tim4.split('-')
                tim2 = int(tim2[0]) * 10 ** 6 + int(tim2[1]) * 10 ** 4 + int(tim2[2]) * 10 ** 2 + int(tim2[3])
                index_lis = [x+1 for x in range(len(date_lis)) if (date_lis[x] >= tim1 and date_lis[x] <= tim2)]
                sorted(index_lis)
                if index_lis:
                    try:
                        tim3 = time.strptime(start_time, '%Y-%m-%d %H:%M:%S')
                        tim3 = time.mktime(tim3)
                        time3 = time.strptime(end_time, '%Y-%m-%d %H:%M:%S')
                        time3 = time.mktime(time3)
                        cur.execute('create table linshi_table as (select * from device_data limit 0);')
                        for i in index_lis:
                            cur.execute("copy linshi_table from '/root/flask_data/{0}' with csv header;".format(lis[i]))
                        cur.execute(
                            "select * from linshi_table where created_on >={0} and created_on <={1} and device_id='{2}';".format(
                                tim3, time3, device_id))
                        data1 = cur.fetchall()
                        cur.execute(
                            "select * from device_data where created_on >={0} and created_on <={1} and device_id='{2}';".format(
                                tim3, time3, device_id))
                        data = cur.fetchall()
                        data += data1
                        cur.execute("drop table linshi_table;")
                        return data
                    except:
                        cur.execute('drop table linshi_table;')
                        return data
        except IndexError:
            print('目录为空！')
            return data
    # def search_sql(start_time, end_time, device_id, cur='', conn=''):
    #     lis = os.listdir('/root/flask_data')
    #     # lis = os.listdir('/Users/mac/Desktop/data')
    #     print(lis)
    #     data = '空'
    #     try:
    #         new_lis = list(map(lambda x: re.findall(r"(.+?)\.", x)[0], lis[1:]))
    #         print(1, new_lis)
    #         if new_lis and start_time and end_time:
    #             data_lis = list(map(lambda x: x.split('-'), new_lis))
    #             print(2, data_lis)
    #             date_lis = [int(x[0]) * 10 ** 6 + int(x[1]) * 10 ** 4 + int(x[2]) * 10 ** 2 + int(x[3]) for x in list(data_lis)]
    #             print(3, date_lis)
    #             begin_time = re.findall(r'(.+?):', start_time)[0].replace(" ", "-")
    #             print(4, begin_time)
    #             tim1 = begin_time.split('-')
    #             tim1 = int(tim1[0]) * 10 ** 6 + int(tim1[1]) * 10 ** 4 + int(tim1[2]) * 10 ** 2 + int(tim1[3])
    #             tim4 = time.strptime(end_time, '%Y-%m-%d %H:%M:%S')
    #             print(5, tim4)
    #             tim4 = time.mktime(tim4) + 3600
    #             tim4 = time.localtime(tim4)
    #             tim4 = time.strftime("%Y-%m-%d-%H", tim4)
    #             print(6, tim4)
    #             tim2 = tim4.split('-')
    #             tim2 = int(tim2[0]) * 10 ** 6 + int(tim2[1]) * 10 ** 4 + int(tim2[2]) * 10 ** 2 + int(tim2[3])
    #             index_lis = [x+1 for x in range(len(date_lis)) if (date_lis[x] >= tim1 and date_lis[x] <= tim2)]
    #             sorted(index_lis)
    #             print(7, index_lis)
    #
    #             if index_lis:
    #                 try:
    #                     print(lis[36], lis[38], lis[56],)
    #                     cur.execute("create table linshi_table as (select * from device_data limit 0);")
    #                     for i in index_lis:
    #                         cur.execute("copy linshi_table from '/root/flask_data/{0}' with csv header;".format(lis[i]))
    #                     tim3 = time.strptime(start_time, '%Y-%m-%d %H:%M:%S')
    #                     tim3 = time.mktime(tim3)
    #                     print(8, tim3)
    #                     time3 = time.strptime(end_time, '%Y-%m-%d %H:%M:%S')
    #                     time3 = time.mktime(time3)
    #                     print(9, time3)
    #                     cur.execute(
    #                         "select * from linshi_table where created_on >={0} and created_on <={1} and device_id='{2}';".format(
    #                             tim3, time3, device_id))
    #                     data = cur.fetchall()
    #                     return data
    #                 except:
    #                     return data
    #     except IndexError:
    #         print('目录为空！')
    #         return data


    # # TODO：将csv文件中的数据恢复，并将符合查询条件的设备信息返回
    # @staticmethod
    # @cur_p
    # # def search_sql(start_time, end_time, device_id, device_id1, cur='', conn=''):
    # #     lis = os.listdir('/flask_data')
    # #     data = '空'
    # #     try:
    # #         new_lis = map(lambda x: re.findall(r"(.+?)\.", x)[0], lis)
    # #     except IndexError:
    # #         print('目录为空！')
    # #         return data
    # #     if new_lis and start_time and end_time:
    # #         data_lis = map(lambda x: x.split('-'), new_lis)
    # #         date_lis = [int(x[0]) * 10 ** 6 + int(x[1]) * 10 ** 4 + int(x[2]) * 10 ** 2 + int(x[3]) for x in
    # #                     list(data_lis)]
    # #         begin_time = re.findall(r'(.+?):', start_time)[0].replace(" ", "-")
    # #         tim1 = begin_time.split('-')
    # #         tim1 = int(tim1[0]) * 10 ** 6 + int(tim1[1]) * 10 ** 4 + int(tim1[2]) * 10 ** 2 + int(tim1[3])
    # #         tim4 = time.strptime(end_time, '%Y-%m-%d %H:%M:%S')
    # #         tim4 = time.mktime(tim4)+3600
    # #         tim4= time.localtime(tim4)
    # #         tim4 = time.strftime("%Y-%m-%d-%H", tim4)
    # #         tim2 = tim4.split('-')
    # #         tim2 = int(tim2[0]) * 10 ** 6 + int(tim2[1]) * 10 ** 4 + int(tim2[2]) * 10 ** 2 + int(tim2[3])
    # #         index_lis = [x for x in range(len(date_lis)) if date_lis[x] >= tim1 and date_lis[x] <= tim2]
    # #         sorted(index_lis)
    # #         if index_lis:
    # #             try:
    # #                 cur.execute('create table linshi_table as( select * from  device_data_data limit 0);')
    # #                 for i in index_lis:
    # #                     cur.execute("copy linshi_table from '/flask_data/{0}' with csv header;".format(
    # #                         lis[i]))
    # #                 tim3 = time.strptime(start_time, '%Y-%m-%d %H:%M:%S')
    # #                 tim3 = time.mktime(tim3)
    # #                 cur.execute(
    # #                     'select * from linshi_table where created_on >={0} and created_on <={1} and device_id={2};'.format(
    # #                         tim3, tim4, "'" + device_id + "'"))
    # #                 data = cur.fetchall()
    # #                 if device_id1:
    # #                     cur.execute(
    # #                         'select * from linshi_table where created_on >={0} and created_on <={1} and device_id={2};'.format(
    # #                             tim3, tim4, "'" + device_id + "'"))
    # #                     data1 = cur.fetchall()
    # #                     data.extend(data1)
    # #                 cur.execute("drop table linshi_table;")
    # #
    # #             except:
    # #                 cur.execute("drop table linshi_table;")
    # #                 return data
    # #     return data
    # def search_sql(start_time, end_time, device_id, device_id1, cur='', conn=''):
    #     lis = os.listdir('/root/flask_data')
    #     # lis = os.listdir('/Users/mac/Desktop/data')
    #     data = '空'
    #     try:
    #         new_lis = list(map(lambda x: re.findall(r"(.+?)\.", x)[0], lis[1:]))
    #         if new_lis and start_time and end_time:
    #             data_lis = list(map(lambda x: x.split('-'), new_lis))
    #             date_lis = [int(x[0]) * 10 ** 6 + int(x[1]) * 10 ** 4 + int(x[2]) * 10 ** 2 + int(x[3]) for x in list(data_lis)]
    #             begin_time = re.findall(r'(.+?):', start_time)[0].replace(" ", "-")
    #             tim1 = begin_time.split('-')
    #             tim1 = int(tim1[0]) * 10 ** 6 + int(tim1[1]) * 10 ** 4 + int(tim1[2]) * 10 ** 2 + int(tim1[3])
    #             tim4 = time.strptime(end_time, '%Y-%m-%d %H:%M:%S')
    #             tim4 = time.mktime(tim4) + 3600
    #             tim4 = time.localtime(tim4)
    #             tim4 = time.strftime("%Y-%m-%d-%H", tim4)
    #             tim2 = tim4.split('-')
    #             tim2 = int(tim2[0]) * 10 ** 6 + int(tim2[1]) * 10 ** 4 + int(tim2[2]) * 10 ** 2 + int(tim2[3])
    #             index_lis = [x+1 for x in range(len(date_lis)) if date_lis[x] >= tim1 and date_lis[x] <= tim2]
    #             sorted(index_lis)
    #             if index_lis:
    #                 try:
    #                     cur.execute('create table linshi_table as (select * from device_data limit 0);')
    #                     for i in index_lis:
    #                         # cur.execute("copy linshi_table from '/Users/mac/Desktop/data/{0}' with csv header;".format(lis[i]))
    #                         cur.execute(
    #                             "copy linshi_table from '/root/flask_data/{0}' with csv header;".format(lis[i]))
    #                     tim3 = time.strptime(start_time, '%Y-%m-%d %H:%M:%S')
    #                     tim3 = time.mktime(tim3)
    #                     time3 = time.strptime(end_time, '%Y-%m-%d %H:%M:%S')
    #                     time3 = time.mktime(time3)
    #                     # tim44 = time.strptime(end_time, '%Y-%m-%d %H:%M:%S')
    #                     # print(tim44)
    #                     # tim44 = time.mktime(tim44)
    #                     # print(tim44)
    #                     # cur.execute(
    #                     #     'select * from linshi_table where created_on >={0} and created_on <={1} and device_id={2};'.format(
    #                     #         tim3, time3, "'" + device_id + "'"))
    #                     cur.execute(
    #                         "select * from linshi_table where created_on >={0} and created_on <={1} and device_id='{}';".format(
    #                             tim3, time3, device_id))
    #                     data = cur.fetchall()
    #                     # print('data', data[0]['id'])
    #                     if device_id1:
    #                         cur.execute(
    #                             'select * from linshi_table where created_on >={0} and created_on <={1} and device_id={2};'.format(
    #                                 tim3, time3, "'" + device_id1 + "'"))
    #                         data1 = cur.fetchall()
    #                         data.extend(data1)
    #                     cur.execute("drop table linshi_table;")
    #                     print(data)
    #                     return data
    #                 except:
    #                     cur.execute("drop table linshi_table;")
    #                     return data
    #     except IndexError:
    #         print('目录为空！')
    #         return data
    # TODO：多表查询设备编号、x坐标、 y坐标、 z坐标，房间名称， 建筑名称
    @staticmethod
    @cur_p
    def get_data(data, cur='', conn=''):
        lis = []
        for i in data:
            try:
                cur.execute(
                    "select e.name,d.x,d.y,d.z,r.name,b.name  from prison_equipment as e,prison_room as "
                    "r,prison_building as b ,device_data as d where e.name='aaa' and e.equipment_room=r.id "
                    "and r.room_building=b.id;")
                data1 = cur.fetchall()
                lis.extend(data1)
            except psycopg2.Error:
                return ''
        return lis

    # TODO：判断设备实施信息是否存在报警，如存在则将报警信息存入报警表中
    @staticmethod
    @cur_p
    def alarm(data,cur='',conn=''):
        lis1 = [{'name': i['device_id'], 'warn_id':i['username'], 'warn_x':i['x'], 'warn_y':i['y'], 'warn_z':i['z'],
                'alarm_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(i['created_on']))), 'alarm_level':'commonly'} for i in data if i['warning'] == 1]
        lis2 = [{'name': i['device_id'],'warn_id':i['username'], 'warn_x': i['x'], 'warn_y': i['y'], 'warn_z': i['z'],
                'alarm_time': i['created_on'], 'alarm_level': 'urgent'} for i in data if i['warning'] == 2]
        lis3 = [{'name': i['device_id'],'warn_id':i['username'], 'warn_x': i['x'], 'warn_y': i['y'], 'warn_z': i['z'],
                'alarm_time': i['created_on'], 'alarm_level': 'very_serious'} for i in data if i['warning'] == 3]
        lis1.extend(lis2)
        lis1.extend(lis3)
        print(lis1)
        res = FlaskAPI.write(lis1, 'prison_warn')
        if res == 'error':
            return res
        else:
            return 'success'

    # TODO: 查跟随组表判断是否存在state = agree的跟随组
    @staticmethod
    @cur_p
    def get_data1(cur='',conn=''):
        try:
            cur.execute(
                "select id,boss_eq from prison_following_group where state='agree';"
            )
            res = cur.fetchall()
            if res:
                return res
        except psycopg2.Error:
            return ''

    # TODO: 根据跟随组表id查prison_manager_following_group中group_id
    @staticmethod
    @cur_p
    def get_data2(data, cur='',conn=''):
        try:
            cur.execute(
                "select group_id from prison_manager_following_group where manager_id = {};".format(data)
            )
            res = cur.fetchall()
            if res:
                return res
        except psycopg2.Error:
            return ''

    # TODO: 根据prison_manager_following_group中group_id查prisoner_manager中的bracelet_id
    @staticmethod
    @cur_p
    def get_data3(data, cur='',conn=''):
        try:
            cur.execute(
                "select bracelet_id from prisoner_manager where id = {};".format(data)
            )
            res = cur.fetchall()
            if res:
                return res
        except psycopg2.Error:
            return ''

    # TODO: 根据prisoner_manager中的bracelet_id查prison_equipment中的name
    @staticmethod
    @cur_p
    def get_data4(data, cur='', conn=''):
        try:
            cur.execute(
                "select name from equipment_bracelet where id = {};".format(data)
            )
            res = cur.fetchall()
            if res:
                return res
        except psycopg2.Error:
            return ''

    # TODO: 根据prison_following_group中的boss_eq查equipment.chest.card中的name
    @staticmethod
    @cur_p
    def get_data44(data, cur='', conn=''):
        try:
            cur.execute(
                "select name from equipment_chest_card where id = {};".format(data)
            )
            res = cur.fetchall()
            if res:
                return res
        except psycopg2.Error:
            return ''

    # TODO: 获取电子围栏的id
    @staticmethod
    @cur_p
    def get_eid(cur='', conn=''):
        try:
            cur.execute(
                "select id from electronic_fence;"
            )
            res = cur.fetchall()
            if res:
                return res
        except psycopg2.Error:
            return ''

    # TODO: 根据电子围栏id获取黑名单中狱警、犯人
    @staticmethod
    @cur_p
    def get_pid(data, table, cur='', conn=''):
        try:
            cur.execute(
                "select prison_black_id from {0} where black_id = {1};".format(table, data)
            )
            res = cur.fetchall()
            if res:
                return res
        except psycopg2.Error:
            return ''

    # TODO: 根据黑名单犯人、狱警prison_black_id查手环设备名称
    @staticmethod
    @cur_p
    def get_e_name(data, table, cur='', conn=''):
        try:
            cur.execute(
                "select name from equipment_bracelet where id = (select bracelet_id from {0} where "
                "id = {1});".format(table, data)
            )
            res = cur.fetchall()
            if res:
                return res
        except psycopg2.Error:
            return ''

    # TODO: 根据黑名单狱警prison_black_id查手环设备名称
    @staticmethod
    @cur_p
    def get_e_name1(data, table, cur='', conn=''):
        try:
            cur.execute(
                "select name from equipment_chest_card where id = (select chest_card_id from {0} where "
                "id = {1});".format(table, data)
            )
            res = cur.fetchall()
            if res:
                return res
            # else:
            #     return 'null'
        except psycopg2.Error:
            return ''



    # TODO:1111
    @staticmethod
    @cur_p
    def get_111(cur='', conn=''):
        try:
            cur.execute(
                "select equipment_x,equipment_y,equipment_z from prison_equipment where name = 'sh008';"
            )
            res = cur.fetchall()
            if res:
                return res
        except psycopg2.Error:
            return ''

    # TODO: 清洗数据再插入
    @staticmethod
    @cur_p
    def rinse_insert(data, table, cur='', conn=''):
        # print(data, table)
        try:
            cur.execute('DELETE from {0};'.format(table))
            res1 = FlaskAPI.deal_data(data)
            if res1 == 'error':
                print("+++++++++++++++")
                return res1
            else:
                try:
                    cur.execute("insert into {0} {1} values{2};".format(table, res1[0], res1[1]))
                    return 'success'
                except psycopg2.Error as e:
                    print('错误原因：', e)
                    return 'error'
        except psycopg2.Error:
            return ''

    # TODO: 查询所有信息
    @staticmethod
    @cur_p
    def query_data(cur='', conn=''):
        sql = "select id from prison_room"
        sql_pe = "select pr.id,pe.id from prison_equipment pe inner join prison_room pr on pe.equipment_room = pr.id;"
        sql_pm = "select pr.id,pm.id from prisoner_manager pm inner join prison_room pr on pm.room_number = pr.id;"
        sql_pp = "select pr.id,pp.id from prison_work_person pp inner join prison_room pr on pp.room_number = pr.id;"
        try:
            cur.execute(sql)
            result = cur.fetchall()
            print("result", result)
            cur.execute(sql_pe)
            result_pe = cur.fetchall()
            print("result_pe", result_pe)
            cur.execute(sql_pm)
            result_pm = cur.fetchall()
            print("result_pm", result_pm)
            cur.execute(sql_pp)
            result_pp = cur.fetchall()
            print("result_pp", result_pp)
            all = {}
            for i in result:
                li = [] #
                all_li = []
                all_eq = {}
                li_1 = []  #
                all_eq_1 = {}
                li_2 = []
                all_eq_2 = {}
                for k in result_pe:
                    if k["id"] == i["id"]:
                        li.append(k["id"])
                        print(li)
                all_eq['设备'] = li
                all_li.append(all_eq)
                for k in result_pm:
                    if k["id"] == i["id"]:
                        li_1.append(k["id"])
                        print(li_1)
                all_eq_1['犯人'] = li_1
                all_li.append(all_eq_1)
                for k in result_pp:
                    if k["id"] == i["id"]:
                        li_2.append(k["id"])
                        print(li_2)
                all_eq_2['狱警'] = li_2
                all_li.append(all_eq_2)
                all[i["id"]] = all_li
            print(all)
            result = json.dumps(all, ensure_ascii=False)
            return result
        except:
            return 'error'


 # TODO: 实时状态信息插入
    @staticmethod
    @cur_p
    def state_data_insert(data, cur='', conn=''):
        try:
            res = FlaskAPI.deal_data(data)
            if res == 'error':
                return res
            else:
                try:
                    cur.execute("insert into state_table {0} values {1};".format(res[0], res[1]))
                    return 'success'
                except psycopg2.Error as e:
                    print('错误原因：', e)
                    return 'error'
        except psycopg2.Error:
            return ''

    # TODO: 打卡信息插入
    @staticmethod
    @cur_p
    def punchCard_data_insert(data, cur='', conn=''):
        try:
            res = FlaskAPI.deal_data(data)
            if res == 'error':
                return res
            else:
                try:
                    cur.execute("insert into fresh_table {0} values {1};".format(res[0], res[1]))
                    return 'success'
                except psycopg2.Error as e:
                    print('错误原因：', e)
                    return 'error'
        except psycopg2.Error:
            return ''



    # TODO: update设备操作表
    @staticmethod
    @cur_p
    def state_data_update(data, table, cur='', conn=''):
        try:
            print(data['state'], data['name'])
            cur.execute("update {0} set state='{1}' where name='{2}';".format(table, data['state'], data['name']))
            return 'success'
        except psycopg2.Error as e:
            print('错误原因：', e)
            return 'error'


    # TODO：根据人员建筑查房间
    @staticmethod
    @cur_p
    def query_room_floor(data, cur='', conn=''):
        try:
            cur.execute(
                "select * from prison_room where room_building = (select id from prison_building where name = '{0}')".format(data))
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print('错误原因：', e)
            return 'error'

    # TODO：根据人员建筑查楼道
    @staticmethod
    @cur_p
    def query_corridor_floor(data, cur='', conn=''):
        try:
            cur.execute(
                "select * from prison_corridor where corridor_building = (select id from prison_building where name = '{0}')".format(data))
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print('错误原因：', e)
            return 'error'


# ========================================================================

    # TODO : 查询告警程度信息 By Wang
    @staticmethod
    @cur_p
    def search_alarm_rule_for_cb(cur='', conn=''):
        try:
            sql = "SELECT id,name FROM prisoner_alarm_rule"
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'


    # TODO : 查询告警详细信息 By Wang
    @staticmethod
    @cur_p
    def search_warn_for_cb(cur='', conn=''):
        try:
            sql = "SELECT alarm_time,warn_id,warning_message,remark,alarm_level FROM prison_warn"
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'


    # TODO 查询设备数量信息 By Wang
    @staticmethod
    @cur_p
    def search_equipments_num_for_cb(cur='', conn=''):
        try:
            sql = "SELECT COUNT(*) FROM equipment_chest_card"
            cur.execute(sql)
            num_of_chestcard = cur.fetchall()[0]['count']
            sql = "SELECT COUNT(*) FROM equipment_bracelet"
            cur.execute(sql)
            num_of_bracelet = cur.fetchall()[0]['count']
            sql = "SELECT COUNT(*) FROM equipment_camera"
            cur.execute(sql)
            num_of_camera = cur.fetchall()[0]['count']
            sql = "SELECT COUNT(*) FROM equipment_base_station"
            cur.execute(sql)
            num_of_base_station = cur.fetchall()[0]['count']
            list_a = [{'name': '胸牌', 'value': num_of_chestcard},
                      {'name': '手环', 'value': num_of_bracelet},
                      {'name': '摄像头', 'value': num_of_camera},
                      {'name': '基站', 'value': num_of_base_station},]

            return list_a

        except:
            return 'error'



    # 查询某一建筑中各个设备的数量
    @staticmethod
    @cur_p
    def counts_of_some_building(building_id, conn='',cur=''):
        cur = conn.cursor()
        sql_dict = {}
        # 基站数量
        sql1 = "SELECT count(*) FROM equipment_base_station where building_control = %s"
        sql_dict['基站'] = sql1
        # 门禁数量
        sql2 = "SELECT count(*) FROM equipment_access_control where building_control = %s"
        sql_dict['门禁'] = sql2
        # 车禁数量
        sql3 = "SELECT count(*) FROM equipment_vehicle_ban where building_control = %s"
        sql_dict['车禁'] = sql3
        # 摄像头数量
        sql4 = "SELECT count(*) FROM equipment_camera where building_control = %s"
        sql_dict['摄像头'] = sql4

        a = []
        for k, v in sql_dict.items():
            b = {}
            data = (building_id,)
            cur.execute(v, data)
            counts = cur.fetchone()[0]
            b['name'] = k
            b['value'] = int(counts)
            a.append(b)
        return a


    # TODO: 查询实时数据中在建筑人员
    # cur.execute(
    #     "select * from prison_corridor where corridor_building = (select id from prison_building where name = '{0}')".format(
    #         data))
    # res = cur.fetchall()
    # return res
    # @staticmethod
    # @cur_p
    # def query_number_person(cur='', conn=''):
    #     try:
    #         cur.execute("select ")
    #     except:
    #         return 'error'

        # ==============================
    # TODO : 根据手环查人员信息
    @staticmethod
    @cur_p
    def search_person_info(data, cur='', conn=''):
        try:
            sql = "select name from prison_work_person where chest_card_id=(SELECT id FROM equipment_chest_card where name = '{0}')".format(data)
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'


    # TODO: 轨迹
    @staticmethod
    @cur_p
    def getguiji(device_id, create_time, end_time, cur='', conn=''):
        try:
            sql = "select x,y,z from device_data where device_id = '{0}' and created_on >='{1}' and " \
                  "created_on <='{2}' order by created_on asc;".format(device_id, create_time, end_time)
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'

    # TODO: 手环历史
    @staticmethod
    @cur_p
    def getequiptment(device_id, create_time, end_time, cur='', conn=''):
        try:
            sql = "select * from device_data where device_id = '{0}' and created_on >='{1}' and " \
                  "created_on <='{2}' order by created_on asc;".format(device_id, create_time, end_time)
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'


# TODO : 根据建筑查人员数量
    @staticmethod
    @cur_p
    def query_person_building(data, cur='', conn=''):
        try:
            sql = "select COUNT(*) from device_data_copy where building='{0}';".format(data)
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'

    # TODO : 根据建筑查人员数量
    @staticmethod
    @cur_p
    def query_person_building_nul(cur='', conn=''):
        try:
            sql = "select COUNT(*) from device_data_copy where building='';"
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'


# # TODO : 根据建筑查人员数量
#     @staticmethod
#     @cur_p
#     def query_person_name_building(data, cur='', conn=''):
#         try:
#             sql = "select username from device_data where building='{0}' and created_on = (select max(created_on) from device_data);".format(
#                 data)
#             cur.execute(sql)
#             res = cur.fetchall()
#             return res
#         except psycopg2.Error as e:
#             print(e)
#             return 'error'


# # TODO : 根据建筑楼层查人员数量
#     @staticmethod
#     @cur_p
#     def query_person_floor(data, cur='', conn=''):
#         try:
#             sql = "select COUNT(*) from device_data where floor='{0}' and created_on = (select max(created_on) from device_data);".format(data)
#             cur.execute(sql)
#             res = cur.fetchall()
#             return res
#         except psycopg2.Error as e:
#             print(e)
#             return 'error'

# TODO : 根据建筑房间查人员数量
    @staticmethod
    @cur_p
    def query_person_room(data1, data2, cur='', conn=''):
        try:
            sql = "select COUNT(*) from device_data_copy where room='{0}' and building='{1}';".format(data1, data2)
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'

# TODO: 查询实时数据中各人员类型数量
    @staticmethod
    @cur_p
    def query_person_number(data, cur='', conn=''):
        try:
            sql = "select COUNT(*) from device_data_copy where ptype='{0}';".format(data)
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'


# # TODO: 查询实时数据中各人员类型名称
#     @staticmethod
#     @cur_p
#     def query_person_nike(data, time, cur='', conn=''):
#         try:
#             sql = "select COUNT(*) from device_data where ptype='{0}' and created_on='{1}'".format(data, time)
#             cur.execute(sql)
#             res = cur.fetchall()
#             return res
#         except psycopg2.Error as e:
#             print(e)
#             return 'error'
# TODO: 人员类型实时数据刷新
    @staticmethod
    @cur_p
    def query_person_details(data, cur='', conn=''):
        try:

            sql = "select username, device_id from device_data_copy where ptype = '{0}'".format(data)
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'


# TODO: ERP狱警人员信息统计
    @staticmethod
    @cur_p
    def query_person_work(cur='', conn=''):
        try:

            sql = "select name from prison_work_person"
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'

# TODO: ERP狱警人员信息统计
    @staticmethod
    @cur_p
    def query_person_prison(cur='', conn=''):
        try:
            sql = "select name from prisoner_manager"
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'

# TODO: ERP狱警人员信息统计
    @staticmethod
    @cur_p
    def query_person_migrantsclass(cur='', conn=''):
        try:

            sql = "select name from prison_migrantsclass"
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'

# TODO: 查询数据库中所有记录建筑名称
    @staticmethod
    @cur_p
    def query_allbuilding(cur='', conn=''):
        try:
            sql = "select id,name from prison_building"
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'


# TODO: 查询数据库中所有记录建筑名称
    @staticmethod
    @cur_p
    def query_room_list(data, cur='', conn=''):
        try:
            sql = "select id,name from prison_room where room_building='{0}'".format(data)
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'


# # TODO: 查询数据库中所有记录建筑名称
#     @staticmethod
#     @cur_p
#     def query_floor_list(data, cur='', conn=''):
#         try:
#             sql = "select id,name from prison_corridor where corridor_building='{0}'".format(data)
#             cur.execute(sql)
#             res = cur.fetchall()
#             return res
#         except psycopg2.Error as e:
#             print(e)
#             return 'error'


# TODO: 根据建筑楼层查人员数量
    @staticmethod
    @cur_p
    def query_person_floorss(cur='', conn=''):
        try:
            sql = "select id, building, floor, count(floor) from device_data_copy group by floor, building, id;"
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'

# TODO：根据建筑楼层查人员名称



# TODO: 根据点击时间获取该时间下的所有人员信息
    @staticmethod
    @cur_p
    def person_list_query(cur='', conn=''):
        try:
            # sql = "select username, device_id, x, z, y, model_url from device_data where created_on='{0}'".format(time)
            sql = "select username, device_id, x, z, y, model_url from device_data_copy;"
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'

# 实时数据人员类型 姓名编号
    @staticmethod
    @cur_p
    def realtime_info_query(cur='', conn=''):
        try:
            sql = "select ptype, username from device_data_copy;"
            # sql = "select ptype, username from device_data where created_on='{0}'".format(time)
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'

# 实时数据人员类型 姓名编号
    @staticmethod
    @cur_p
    def realtimes_info_query(data, cur='', conn=''):
        try:
            sql = "select username, device_id, id, ptype from device_data_copy where username like '%{0}%';".format(data)
            # sql = "select ptype, username from device_data where created_on='{0}'".format(time)
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'

# 人员搜索
    @staticmethod
    @cur_p
    def realtime_allinfo(d2, cur='', conn=''):
        try:
            sql = "select device_id, ptype, username, id from device_data_copy where username like '%{0}%' limit 1;".format(d2)
            cur.execute(sql)
            res = cur.fetchall()
            # sql1 = "select * from prison_work_person where name like '{0}' limit 1;".format(d2)
            # cur.execute(sql1)
            # res1 = cur.fetchall()
            # sql = "select ptype, username from device_data where created_on='{0}'".format(time)
            # res = res + res1
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'

#
# # 根据狱警姓名查询相关信息
#     @staticmethod
#     @cur_p
#     def realtime_allinfo1(d2, cur='', conn=''):
#         try:
#             sql = "select device_id, username, id, (1) as column  from device_data where created_on = (select max(created_on) from device_data) and username like '%{0}%' and ptype='1';".format(d2)
#             cur.execute(sql)
#             res = cur.fetchall()
#             # sql1 = "select * from prison_work_person where name like '{0}' limit 1;".format(d2)
#             # cur.execute(sql1)
#             # res1 = cur.fetchall()
#             # sql = "select ptype, username from device_data where created_on='{0}'".format(time)
#             # res = res + res1
#             return res
#         except psycopg2.Error as e:
#             print(e)
#             return 'error'

# # 根据犯人姓名查询相关信息
#     @staticmethod
#     @cur_p
#     def realtime_allinfo2(d2, cur='', conn=''):
#         try:
#             sql = "select device_id, username, id, (2) as column  from device_data where created_on = (select max(created_on) from device_data) and username like '%{0}%' and ptype='2';".format(d2)
#             cur.execute(sql)
#             res = cur.fetchall()
#             # sql1 = "select * from prisoner_manager where name like '%{0}%' limit 1;".format(d2)
#             # cur.execute(sql1)
#             # res1 = cur.fetchall()
#             # sql = "select ptype, username from device_data where created_on='{0}'".format(time)
#             # res = res + res1
#             return res
#         except psycopg2.Error as e:
#             print(e)
#             return 'error'

# # 根据外来人员姓名查询相关信息
#     @staticmethod
#     @cur_p
#     def realtime_allinfo3(d2, cur='', conn=''):
#         try:
#             sql = "select device_id, username, id, (3) as column  from device_data where created_on = (select max(created_on) from device_data) and username like '%{0}%' and ptype='3';".format(d2)
#             cur.execute(sql)
#             res = cur.fetchall()
#             # sql1 = "select * from prison_migrantsclass where name = '{0}' limit 1;"
#             # cur.execute(sql1)
#             # res1 = cur.fetchall()
#             # sql = "select ptype, username from device_data where created_on='{0}'".format(time)
#             # res = res + res1
#             return res
#         except psycopg2.Error as e:
#             print(e)
#             return 'error'

# 查询人员-狱警
    @staticmethod
    @cur_p
    def qpwp(cur='', conn=''):
        try:
            sql = "select chest_card_id, id, name, (1) as column  from prison_work_person order by id ASC;"
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'

# 查询device_id
    @staticmethod
    @cur_p
    def query_device_id(data, cur='', conn=''):
        try:
            sql = "select name from equipment_chest_card where id = '{0}';".format(data)
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'

# 查询device_id
    @staticmethod
    @cur_p
    def query_device_id1(data, cur='', conn=''):
        try:
            sql = "select name from equipment_bracelet where id = '{0}';".format(data)
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'

# 查询人员-犯人
    @staticmethod
    @cur_p
    def qpm(cur='', conn=''):
        try:
            sql = "select bracelet_id, id,name,(2) as column  from prisoner_manager order by id ASC;"
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'

# 查询人员-外来人员
    @staticmethod
    @cur_p
    def qpms(cur='', conn=''):
        try:
            sql = "select bracelet_id, id,name,(3) as column from prison_migrantsclass order by id ASC;"
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'



# # 查询实时设备数量
#     @staticmethod
#     @cur_p
#     def realtimedevice(cur='', conn=''):
#         try:
#             sql = "select COUNT(*) from state_table where time = (select max(time) from state_table);"
#             cur.execute(sql)
#             res = cur.fetchall()
#             return res
#         except psycopg2.Error as e:
#             print(e)
#             return 'error'

# 模糊查询所有设备
    @staticmethod
    @cur_p
    def sbAll(data, data1, data2, cur='', conn=''):
        try:
            sql = "select name,({0}) as column from {1} where name like '%{2}%';".format(data,data1,data2)
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'

# 查询设备--基站
    @staticmethod
    @cur_p
    def qebs(cur='', conn=''):
        try:
            sql = "select name,(1) as column from equipment_base_station order by id ASC;"
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'


# 查询设备--门禁
    @staticmethod
    @cur_p
    def qeac(cur='', conn=''):
        try:
            sql = "select name,(2) as column from equipment_access_control order by id ASC;"
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'

# 查询设备--车禁
    @staticmethod
    @cur_p
    def qevb(cur='', conn=''):
        try:
            sql = "select name,(3) as column from equipment_vehicle_ban order by id ASC;"
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'

# 查询设备--周界
    @staticmethod
    @cur_p
    def qp(cur='', conn=''):
        try:
            sql = "select name,(4) as column from equipment_perimeter order by id ASC;"
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'

# 查询设备--摄像头
    @staticmethod
    @cur_p
    def qc(cur='', conn=''):
        try:
            sql = "select name,(5) as column from equipment_camera order by id ASC;"
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'

# 查询设备-一键报警
    @staticmethod
    @cur_p
    def qecp(cur='', conn=''):
        try:
            sql = "select name,(6) as column from equipment_call_police order by id ASC;"
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'

# 查询设备-车载摄像头
    @staticmethod
    @cur_p
    def qecc(cur='', conn=''):
        try:
            sql = "select name,(7) as column from equipment_car_camera order by id ASC;"
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'

# 查询设备-胸牌
    @staticmethod
    @cur_p
    def qecca(cur='', conn=''):
        try:
            sql = "select name,(8) as column from equipment_chest_card order by id ASC;"
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'

# 查询设备-手环
    @staticmethod
    @cur_p
    def qeba(cur='', conn=''):
        try:
            sql = "select name,(9) as column from equipment_bracelet order by id ASC;"
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'

# 查询设备-车辆
    @staticmethod
    @cur_p
    def qeca(cur='', conn=''):
        try:
            sql = "select name,(10) as column from equipment_car order by id ASC;"
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'

# 设备搜索
    @staticmethod
    @cur_p
    def realtimes_device_query(data, cur='', conn=''):
        try:
            sql = "select name, state from state_table_copy where name like '%{0}%';".format(
                data)
            # sql = "select ptype, username from device_data where created_on='{0}'".format(time)
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'


# 设备搜索
    @staticmethod
    @cur_p
    def querystates(cur='', conn=''):
        try:
            sql = "select name,state from state_table_copy;"
            # sql = "select ptype, username from device_data where created_on='{0}'".format(time)
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'

# 根据设备名称查找设备状态
    @staticmethod
    @cur_p
    def querystateone(data, cur='', conn=''):
        try:
            sql = "select state from state_table_copy where name = '{0}';".format(data)
            # sql = "select ptype, username from device_data where created_on='{0}'".format(time)
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'

# TODO: 查询实时数据中各设备类型数量
    @staticmethod
    @cur_p
    def query_device_number(data, cur='', conn=''):
        try:
            sql = "select COUNT(*) from state_table_copy where name like '{0}%';".format(data)
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'

# TODO: 查询实时数据中总数量
    @staticmethod
    @cur_p
    def query_device_allnumber(cur='', conn=''):
        try:
            sql = "select COUNT(*) from state_table_copy;"
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'

# TODO: 查询实时数据中各设备类型数量
    @staticmethod
    @cur_p
    def query_device_alarm(cur='', conn=''):
        try:
            sql = "select name, device_id, alarm_x, alarm_y, alarm_z, time, details from historical_alarm_copy;"
            # sql = "select COUNT(*) from state_table where name like '{0}%' and time=(select max(time) from state_table);".format(data)
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'

# TODO:设备编号搜索
    @staticmethod
    @cur_p
    def realtimes_deviceinfo_query(data, cur='', conn=''):
        try:
            sql = "select name, device_id, alarm_x, alarm_y, alarm_z, time, details from historical_alarm_copy where device_id like '%{0}%';".format(data)
            # sql = "select ptype, username from device_data where created_on='{0}'".format(time)
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'

# TODO:查询条件触发告警搜索ConditionAlarmFind
    @staticmethod
    @cur_p
    def conditionalarmfind(data, data1, cur='', conn=''):
        try:
            sql = "select name, warn_id, type, alarm_level, alarm_time from prison_warn where name like '%{0}%'limit 10 offset {1};".format(
                data, data1)
            # sql = "select ptype, username from device_data where created_on='{0}'".format(time)
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'

    # TODO:查询条件触发告警搜索ConditionAlarmFind
    @staticmethod
    @cur_p
    def conditionalarmfindnum(data, cur='', conn=''):
        try:
            sql = "select count(*) from prison_warn where name like '%{0}%'".format(
                data)
            # sql = "select ptype, username from device_data where created_on='{0}'".format(time)
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'

# # TODO:设备编号搜索
#     @staticmethod
#     @cur_p
#     def realtimes_deviceinfo_querys(data1, data2, cur='', conn=''):
#         try:
#             sql = "select name, device_id, alarm_x, alarm_y, alarm_z, time, details from historical_alarm_copy where device_id like '%{0}%' limit 10 offset {1};".format(
#                 data1, data2)
#             # sql = "select ptype, username from device_data where created_on='{0}'".format(time)
#             cur.execute(sql)
#             res = cur.fetchall()
#             return res
#         except psycopg2.Error as e:
#             print(e)
#             return 'error'

# # TODO: 获取总条数
#     @staticmethod
#     @cur_p
#     def realtimes_deviceinfo_query_numbers(data, cur='', conn=''):
#         try:
#             sql = "select count(*) from historical_alarm_copy where device_id like '%{0}%';".format(data)
#             # sql = "select ptype, username from device_data where created_on='{0}'".format(time)
#             cur.execute(sql)
#             res = cur.fetchall()
#             return res
#         except psycopg2.Error as e:
#             print(e)
#             return 'error'


# TODO:设备分类数据展示
    @staticmethod
    @cur_p
    def device_data_show(data, cur='', conn=''):
        try:
            sql = "select name from {0};".format(data)
            # sql = "select ptype, username from device_data where created_on='{0}'".format(time)
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'

# TODO:设备编号列表
    @staticmethod
    @cur_p
    def realtimes_deviceinfo_list(data, cur='', conn=''):
        try:
            sql = "select name, device_id, alarm_x, alarm_y, alarm_z, time, details from historical_alarm_copy limit 10 offset {0};".format(data)
            # sql = "select ptype, username from device_data where created_on='{0}'".format(time)
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)

    # TODO:设备编号列表
    @staticmethod
    @cur_p
    def realtimes_deviceinfo_lists(cur='', conn=''):
        try:
            sql = "select name, device_id, alarm_x, alarm_y, alarm_z, time, details from historical_alarm_copy;"
            # sql = "select ptype, username from device_data where created_on='{0}'".format(time)
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)

    # TODO:设备编号列表
    @staticmethod
    @cur_p
    def truncate_datas(table, cur='', conn=''):
        try:
            sql = "truncate {0};".format(table)
            # sql = "select ptype, username from device_data where created_on='{0}'".format(time)
            cur.execute(sql)
            # FlaskAPI.write(data, table)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)

# TODO: 电子围栏搜索
    @staticmethod
    @cur_p
    def realtimes_fence_query(data, cur='', conn=''):
        try:
            sql = "select name, creation_time, end_time from electronic_fence where name like '%{0}%';".format(data)
            # sql = "select ptype, username from device_data where created_on='{0}'".format(time)
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'


# TODO : 热力图

    # TODO: 查询数据库中所有记录建筑名称
    @staticmethod
    @cur_p
    def query_chart_allbuilding(cur='', conn=''):
        try:
            sql = "select name,building_x,building_y,building_z,building_long,building_wide from prison_building"
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'


    @staticmethod
    @cur_p
    def query_chart_building(data, cur='', conn=''):
        try:
            sql = "select COUNT(*) from device_data_copy where building='{0}';".format(data)
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'

# TODO：跟随组

# TODO: 查跟随组
    @staticmethod
    @cur_p
    def query_follow_group_3D(cur='', conn=''):
        try:
            sql = "select id,name,boss_eq,starting_position,end_position from prison_following_group where state='agree';"
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'

    # TODO: 查跟随组
    @staticmethod
    @cur_p
    def query_follow_group_all(data, cur='', conn=''):
        try:
            sql = "select state, id,name,boss_eq,starting_position,end_position from prison_following_group limit 10 offset {0};".format(data)
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'

    # TODO: 根据跟随组名称查跟随组
    @staticmethod
    @cur_p
    def query_follow_group_by_name(data1, data, cur='', conn=''):
        try:
            sql = "select state, id,name,boss_eq,starting_position,end_position from prison_following_group where name like '%{0}%'limit 10 offset {1};".format(data1, data)
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'

    # TODO: 查狱警组
    @staticmethod
    @cur_p
    def query_follow_group_workman(data, cur='', conn=''):
        try:
            sql = "select group_id from prison_work_person_following_group where person_id='{0}';".format(data)
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'

    # TODO: 查犯人组
    @staticmethod
    @cur_p
    def query_follow_group_prison(data, cur='', conn=''):
        try:
            sql = "select group_id from prison_manager_following_group where manager_id='{0}';".format(data)
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'

    # TODO：找狱警name
    @staticmethod
    @cur_p
    def query_workman_info(data, cur='', conn=''):
        try:
            sql = "select name,chest_card_id from prison_work_person where id='{0}';".format(data)
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'

    # TODO：找犯人name
    @staticmethod
    @cur_p
    def query_prison_info(data, cur='', conn=''):
        try:
            sql = "select name,bracelet_id from prisoner_manager where id='{0}';".format(data)
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'

    # TODO: 查找设备device_id
    @staticmethod
    @cur_p
    def query_workman_device_id(data, cur='', conn=''):
        try:
            sql = "select name from equipment_chest_card where id='{0}';".format(data)
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'

    # TODO: 查找设备device_id
    @staticmethod
    @cur_p
    def query_prison_device_id(data, cur='', conn=''):
        try:
            sql = "select name from equipment_bracelet where id='{0}';".format(data)
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'

    # # TODO: 查犯人组
    # @staticmethod
    # @cur_p
    # def query_follow_group_prisoner(data, cur='', conn=''):
    #     try:
    #         sql = "select group_id from prison_manager_following where manager_id='{0}';".format(data)
    #         cur.execute(sql)
    #         res = cur.fetchall()
    #         return res
    #     except psycopg2.Error as e:
    #         print(e)
    #         return 'error'

    # TODO: 查犯人组
    @staticmethod
    @cur_p
    def query_follow_group_prison(data, cur='', conn=''):
        try:
            sql = "select group_id from prison_manager_following_group where manager_id='{0}';".format(data)
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'


    # 获取当前日期电子围栏告警前十条，不满十条则全部获取 alarm_time, alarm_level, warn_id, name
    @staticmethod
    @cur_p
    def query_fence_alarm(data, cur='', conn=''):
        try:
            sql = "select alarm_time, alarm_level, warn_id, name, type from prison_warn where alarm_time >= '{0}' and type = 'electronic_fence' order by alarm_time DESC limit 10;".format(data)
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'


    # 分页获取所有电子围栏告警的总条数
    @staticmethod
    @cur_p
    def page_fence_alarm_count(data, cur='', conn=''):
        try:
            sql = "select count(*) from prison_warn where type = '{0}';".format(data)
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'

    # 分页获取所有电子围栏告警的十条
    @staticmethod
    @cur_p
    def page_fence_alarm(data, cur='', conn=''):
        try:
            sql = "select alarm_time, alarm_level, warn_id, name, type from prison_warn where type = 'electronic_fence' order by alarm_time DESC limit 10 offset {0};".format(data)
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'

    # 获取当前日期报警前十条，不满十条则全部获取 alarm_time, alarm_level, warn_id, name
    @staticmethod
    @cur_p
    def query_fence_alarms(data, cur='', conn=''):
        try:
            sql = "select alarm_time, alarm_level, warn_id, name, type from prison_warn where alarm_time >= '{0}' order by alarm_time DESC limit 10;".format(
                data)
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'

    # 总条数
    @staticmethod
    @cur_p
    def page_fence_alarms_count(cur='', conn=''):
        try:
            sql = "select count(*) from prison_warn;"
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'


    # 分页获取所有报警的十条
    @staticmethod
    @cur_p
    def page_fence_alarms(data, cur='', conn=''):
        try:
            sql = "select alarm_time, alarm_level, warn_id, name, type from prison_warn order by alarm_time DESC limit 10 offset {0};".format(
                data)
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'

    # 删除告警信息
    @staticmethod
    @cur_p
    def delhisalarm(data, cur='', conn=''):
        try:
            sql = "delete from historical_alarm_copy where device_id = '{0}';".format(
                data)
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'


    # 插入mark_name
    @staticmethod
    @cur_p
    def markinsert(data, cur='', conn=''):
        try:
            res = FlaskAPI.deal_data(data)
            if res == 'error':
                return res
            else:
                try:
                    cur.execute("insert into mark_name {0} values {1};".format(res[0], res[1]))
                    return 'success'
                except psycopg2.Error as e:
                    print('错误原因：', e)
                    return 'error'
        except psycopg2.Error:
            return ''


    # 查看mark_name
    @staticmethod
    @cur_p
    def markquery(table, cur='', conn=''):
        try:
            cur.execute("select * from {0}".format(table))
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print('错误原因：', e)
            return 'error'

    # 删除mark_name
    @staticmethod
    @cur_p
    def markdel(data, cur='', conn=''):
        try:
            cur.execute("delete from mark_name where name='{0}'".format(data))
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print('错误原因：', e)
            return 'error'

    # 判断是否存在name
    @staticmethod
    @cur_p
    def queryforname(data, cur='', conn=''):
        try:
            cur.execute("select * from mark_name where name='{0}'".format(data))
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print('错误原因：', e)
            return 'error'

    # 根据device_id查胸牌id
    @staticmethod
    @cur_p
    def queryidbydeviceid(data, cur='', conn=''):
        try:
            cur.execute("select id from equipment_chest_card where name='{0}'".format(data))
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print('错误原因：', e)
            return 'error'

    # 根据胸牌id查跟随组中状态为agree的boss_eq
    @staticmethod
    @cur_p
    def querystate(data, cur='', conn=''):
        try:
            cur.execute("select id from prison_following_group where boss_eq='{0}' and state='agree';".format(data))
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print('错误原因：', e)
            return 'error'

    # 获取电子围栏
    @staticmethod
    @cur_p
    def query_active_fence(cur='', conn=''):
        try:
            cur.execute("select * from electronic_fence;")
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print('错误原因：', e)
            return 'error'

    # 查询各个设备表中设备的数量
    @staticmethod
    @cur_p
    def query_devicetab_numbers(table, cur='', conn=''):
        try:
            cur.execute("select count(*) from {0};".format(table))
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print('错误原因：', e)
            return 'error'


    # 删除电子围栏
    @staticmethod
    @cur_p
    def fencedel(data, cur='', conn=''):
        try:
            cur.execute("delete from electronic_fence where name='{0}'".format(data))
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print('错误原因：', e)
            return 'error'

    # TODO: 跟随组告警当前一天
    @staticmethod
    @cur_p
    def followalarmtoday(data, type, time, cur='', conn=''):
        try:
            sql = "select alarm_time, alarm_level, warn_id, name, type from prison_warn where alarm_time >= '{0}' and type='{1}' " \
                  "order by alarm_time DESC limit 10 offset {2};".format(time, type, data)
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'

    # TODO: 跟随组告警历史
    # sql = "select alarm_time, alarm_level, warn_id, name, type from prison_warn where alarm_time >= '{0}' order by alarm_time DESC limit 10;".format(
    #                 data)
    @staticmethod
    @cur_p
    def followalarmhistory(data, cur='', conn=''):
        try:
            sql = "select alarm_time, alarm_level, warn_id, name, type from prison_warn where type='alarm_following_group' " \
                  "order by alarm_time DESC limit 10 offset {1};".format(time, data)
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)

    # 告警数量
    @staticmethod
    @cur_p
    def page_fence_alarm_counts(data, time, cur='', conn=''):
        try:
            sql = "select count(*) from prison_warn where type = '{0}' and alarm_time >= '{1}';".format(data, time)
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'

    # 告警数量
    @staticmethod
    @cur_p
    def page_group_counts(cur='', conn=''):
        try:
            sql = "select count(*) from prison_following_group;".format()
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'

    # 最近一次告警数量
    @staticmethod
    @cur_p
    def history_counts(cur='', conn=''):
        try:
            sql = "select count(*) from historical_alarm_copy;"
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'



    # 最近一次告警数量
    @staticmethod
    @cur_p
    def query_camera(data, cur='', conn=''):
        try:
            sql = "select name,control_x,control_y,control_z from {0};".format(data)
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'



    # 获取不同类型告警
    @staticmethod
    @cur_p
    def today_alarm(data, time, cur='', conn=''):
        try:
            sql = "select alarm_time, alarm_level, warn_id, name, type, warn_x, warn_y, warn_z from prison_warn where type = '{0}' and alarm_time >= '{1}';".format(data, time)
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'

    # 建筑id查设备
    @staticmethod
    @cur_p
    def device_building_query_id(data1, data2, cur='', conn=''):
        try:
            sql = "select count(*) from {0} where building_control = '{1}';".format(data1, data2)
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'

    # 房间id查设备
    @staticmethod
    @cur_p
    def device_room_query_id(data1, data2, data3, cur='', conn=''):
        try:
            sql = "select count(*) from {0} where building_control = '{1}' and room_control = '{2}';".format(data1, data2, data3)
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'

    # 建筑id查设备
    @staticmethod
    @cur_p
    def query_null(data1, cur='', conn=''):
        try:
            sql = "select count(*) from {0};".format(data1)
            cur.execute(sql)
            res = cur.fetchall()
            return res
        except psycopg2.Error as e:
            print(e)
            return 'error'