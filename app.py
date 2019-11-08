 # coding:utf-8
from redis_server import *
from redis_sentinel import *
from psy_api import FlaskAPI
import threading
from threading import Thread
import json, time, datetime, random
import threading, math
import sys


# TODO：post方法将json数据插入数据库指定的表中

class Fun1(Resource):
    def post(self, table):
        data = request.json
        dic = {}
        dic['code'] = 200
        dic["msg"] = u"请求错误！"
        dic["success"] = "false"
        begin_time = time.time()
        if data:
            res = FlaskAPI.write(data, table)
            if res == 'error':
                return dic
            else:
                over_time = time.time()
                last_time = over_time - begin_time
                dic["msg"] = u"插入成功"
                dic['success'] = "True"
                dic['usetime'] = last_time
                return dic
        else:
            return dic


# TODO：读取表中所有数据
class Fun2(Resource):
    def get(self, table):
        res = FlaskAPI.read(table)
        if res == 'error':
            return '失败', 200
        else:
            return res, 200


# # TODO：查询围栏表中过期的围栏信息
# class Fun3(Resource):
#     def get(self):
#         now_time = time.time()
#         res = FlaskAPI.read('fence', condition="start_time <= {0} and end_time >={1}".format(now_time, now_time))
#         if res and res != 'error':
#             for i in res:
#                 timeArray = time.localtime(i['start_time'])
#                 i['start_time'] = time.strftime("%Y-%m-%d %H:%M", timeArray)
#                 timeArray = time.localtime(i['end_time'])
#                 i['end_time'] = time.strftime("%Y-%m-%d %H:%M", timeArray)
#         return res


# TODO：设备实时信息插入接口
class Fun4(Resource, Thread):
    def post(self):
        data = request.json
        dic = {}
        dic['code'] = 200
        dic["msg"] = u"请求错误！"
        dic["success"] = "false"
        begin_time = time.time()
        if data:
            # try:
            if data and type(data) == list:
                # 线程1处理数据并存入redis

                def thread1():
                    list1 = []
                    b_m = FlaskAPI.read('prison_boundary',
                                        target_field=["boundary_start_x", "boundary_start_y", "boundary_end_x",
                                                      "boundary_end_y"])
                    # print("b_m", b_m)
                    b_i = FlaskAPI.read('prisoner_alarm_rule', target_field=["alarm_level", "alarm_range"],
                                        condition="name='边界'")
                    # print("b_i", b_i)
                    e_f = FlaskAPI.read('electronic_fence',
                                        target_field=["id", "initial_coordinates_x", "initial_coordinates_y",
                                                      "initial_coordinates_z", "termination_coordinates_x",
                                                      "termination_coordinates_y"])
                    b_g = FlaskAPI.read('prisoner_alarm_rule', target_field=["alarm_level", "alarm_range"],
                                        condition="name='跟随组'")

                    # print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++跟随组", b_g)

                    b_d = FlaskAPI.read('prisoner_alarm_rule', target_field=["alarm_level"],
                                        condition="name='电子围栏告警'")
                    b_y = FlaskAPI.read('prisoner_alarm_rule', target_field=["alarm_level"],
                                        condition="name='硬件状态异常'")
                    b_gg = FlaskAPI.read('prisoner_alarm_rule', target_field=["alarm_level"],
                                        condition="name='工作人员主动触发告警'")
                    #  判断是否有状态==agree的跟随组
                    gd1 = FlaskAPI.get_data1()

                    print("gd11111", gd1)
                    gd_lis = []
                    if gd1 is not None:
                        for j in gd1:
                            if j["boss_eq"] is not None:
                                gd_lis1 = []
                                gd_dic1 = {}
                                # 查询该跟随组中犯人的id
                                gd2 = FlaskAPI.get_data2(j["id"])
                                if gd2 is not None:
                                    for i2 in gd2:
                                        # 查犯人的手环编号
                                        gd3 = FlaskAPI.get_data3(i2["group_id"])
                                        # print("---------------------------------", gd3[0]["bracelet_id"])
                                        if gd3[0]["bracelet_id"] is not None:
                                            # 查手环编号
                                            gd4 = FlaskAPI.get_data4(gd3[0]["bracelet_id"])
                                            print("666666", gd4)
                                            # print("---------------------gd4", gd4)
                                            gd_lis1.append(gd4[0]["name"])
                                    # 根据组长设备查prison_equipment中的name
                                    gd5 = FlaskAPI.get_data44(j["boss_eq"])
                                    print("---------------------------------", gd5)
                                    gd_dic1[gd5[0]["name"]] = gd_lis1

                                    # [["组长设备编号"]:["犯人1设备编号","犯人2设备编号","犯人3设备编号"...]]
                                    gd_lis.append(gd_dic1)
                    dict2 = {}
                    ydata = {}
                    fdata = {}
                    for i in data:
                        print("熊大", i)
                        if i["ptype"] == 1:
                            ydata[i["device_id"]] = i
                        elif i["ptype"] == 2:
                            fdata[i["device_id"]] = i
                    for i in data:
                        if i['username'] != 'null' and i['ptype'] != 'null':
                        # 硬件状态
                            if b_y[0]["alarm_level"] and i["state"] == 0:
                                dict1 = {}
                                dict1["name"] = i['device_id']
                                dict1["warn_id"] = i['username']
                                dict1["warn_x"] = i['x']
                                dict1["warn_y"] = i['y']
                                timeArray = time.localtime(float(i['created_on']))
                                dict1["alarm_time"] = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
                                dict1["alarm_level"] = b_y[0]["alarm_level"]
                                dict1["type"] = 'abnormal'
                                list1.append(dict1)
                            else:
                                # 格式化数据
                                r_x = i['ref_x'] + i['x']
                                r_y = i['ref_y'] + i['y']
                                r_z = i['ref_z'] + i['z']
                                i["r_x"] = r_x
                                i["r_y"] = r_y
                                i["r_z"] = r_z
                                dict2[i["device_id"]] = i

                                # 判断是否是犯人 （1：狱警 2：犯人 3：外来人员）
                                if i['ptype'] == 2:
                                    # 主动触发
                                    if i["warning"] and i["warning"] == 0:
                                        dict1 = {}
                                        dict1["name"] = i['device_id']
                                        dict1["warn_id"] = i['username']
                                        dict1["warn_x"] = i['x']
                                        dict1["warn_y"] = i['y']
                                        timeArray = time.localtime(float(i['created_on']))
                                        dict1["alarm_time"] = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
                                        if b_gg:
                                            if b_gg[0]["alarm_level"] is not None:
                                                dict1["alarm_level"] = b_gg[0]["alarm_level"]
                                            else:
                                                dict1["alarm_level"] = "very_serious"
                                        dict1["type"] = 'person'
                                        list1.append(dict1)
                                    # 边界
                                    if b_m != []:
                                        xlis = [float(b_m[0]["boundary_start_x"]),
                                                 float(b_m[0]["boundary_end_x"])]
                                        ylis = [float(b_m[0]["boundary_start_y"]),
                                                 float(b_m[0]["boundary_end_y"])]
                                        xlis.sort()
                                        ylis.sort()
                                        # print(float(b_i[0]["alarm_range"]))
                                        # print(xlis, xlis[0])
                                        # print("xxx", (xlis[0]+float(b_i[0]["alarm_range"])))
                                        # print((xlis[1]-float(b_i[0]["alarm_range"])))
                                        # print("yyy", (ylis[1]-float(b_i[0]["alarm_range"])))
                                        # print((ylis[0]+float(b_i[0]["alarm_range"])))
                                        if (r_x <= (xlis[0]+float(b_i[0]["alarm_range"]))) or (r_x >= (xlis[1]-float(b_i[0]["alarm_range"])))\
                                                or (r_y <= (ylis[0]+float(b_i[0]["alarm_range"]))) or (r_y >= (ylis[1]-float(b_i[0]["alarm_range"]))):
                                            dict1 = {}
                                            dict1["name"] = i['device_id']
                                            dict1["warn_id"] = i['username']
                                            dict1["warn_x"] = i['x']
                                            dict1["warn_y"] = i['y']
                                            timeArray = time.localtime(float(i['created_on']))
                                            dict1["alarm_time"] = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
                                            if b_i:
                                                if b_i[0]["alarm_level"] is not None:
                                                    dict1["alarm_level"] = b_i[0]["alarm_level"]
                                                else:
                                                    dict1["alarm_level"] = "very_serious"
                                            dict1["type"] = 'alarm_boundary'
                                            list1.append(dict1)
                    # 跟随组判断
                    # ["组长设备编号":["犯人1设备编号","犯人2设备编号","犯人3设备编号"...]]
                    print("dddddd", len(gd_lis))
                    if len(gd_lis) > 0:
                        print("1111111111", gd_lis)
                        for item in gd_lis:
                            print("1111", dict2)
                            for k, v in item.items():
                                print(k, v)
                                if k in dict2.keys():
                                    a = [dict2[k]["r_x"], dict2[k]["r_y"]]
                                    for vv in v:
                                        print("""""""")
                                        b = [dict2[vv]["r_x"], dict2[vv]["r_y"]]
                                        print('0614', math.sqrt((int(a[0]) - int(b[0])) ** 2 + (
                                                    int(a[1]) - int(b[1])) ** 2))
                                        print('0614', int(b_g[0]["alarm_range"]))
                                        if (math.sqrt((int(a[0]) - int(b[0])) ** 2 + (
                                                int(a[1]) - int(b[1])) ** 2)) > int(
                                                b_g[0]["alarm_range"]):
                                            dis1 = {}
                                            dis1["name"] = dict2[vv]["device_id"]
                                            dis1["warn_id"] = dict2[vv]['username']
                                            dis1["warn_x"] = dict2[vv]['x']
                                            dis1["warn_y"] = dict2[vv]['y']
                                            timeArray = time.localtime(
                                                float(dict2[vv]['created_on']))
                                            dis1["alarm_time"] = time.strftime("%Y-%m-%d %H:%M:%S",
                                                                               timeArray)
                                            print("时间啊", dis1["alarm_time"])
                                            dis1["type"] = 'alarm_following_group'
                                            if b_g:
                                                if b_g[0]["alarm_level"] is not None:
                                                    dis1["alarm_level"] = b_g[0]["alarm_level"]
                                                else:
                                                    dis1["alarm_level"] = "very_serious"
                                            list1.append(dis1)
                    # 电子围栏
                    # 获取电子围栏
                    res = FlaskAPI.query_active_fence()
                    eid = []
                    dic_fence = {}
                    # 获取有效的电子围栏
                    for i in res:
                        i["creation_time"] = time.mktime(
                            time.strptime("{0}".format(i['creation_time']), '%Y-%m-%d %H:%M:%S'))
                        i["end_time"] = time.mktime(time.strptime("{0}".format(i['end_time']), '%Y-%m-%d %H:%M:%S'))
                        # 修正时差八小时
                        i['creation_time'] += 60 * 60 * 8
                        i['end_time'] += 60 * 60 * 8
                        if i["creation_time"] <= begin_time and i["end_time"] >= begin_time:
                            eid.append(i["id"])
                            dic_fence[i["id"]] = i
                        print(dic_fence)
                    # 将所有数据进行筛选（狱警&犯人）
                    # print('dict2++++++++++', dict2)
                    # eid = FlaskAPI.get_eid()
                    if len(eid) > 0:
                        for x in eid:
                            a1 = [] # 犯人黑名单
                            a2 = [] # 犯人白名单
                            a3 = [] # 狱警黑名单
                            a4 = [] # 狱警白名单
                            efb_pbi = FlaskAPI.get_pid(table="electronic_fence_black", data=x) # 犯人黑名单
                            print("犯人黑名单", efb_pbi)
                            # print('112233', efb_pbi)
                            pefb_pbi = FlaskAPI.get_pid(table="prison_electronic_fence_black", data=x) # 狱警黑名单
                            print('11223344', pefb_pbi)
                            efw_pbi = FlaskAPI.get_pid(table="electronic_fence_white", data=x)  # 犯人白名单
                            # print('112233', efw_pbi)
                            pefw_pbi = FlaskAPI.get_pid(table="prison_electronic_fence_white", data=x)  # 狱警白名单
                            # print('11223344', pefw_pbi)
                            if efb_pbi:
                                for y in efb_pbi:
                                    ename = FlaskAPI.get_e_name(table="prisoner_manager", data=y["prison_black_id"]) # 犯人黑名单
                                    a1.append(ename[0]["name"])
                                    # print("犯人黑名单111", a1)
                                for l in a1:
                                    # print("犯人黑名单222", fdata)
                                    dict1 = {}
                                    if l in fdata.keys():
                                        if abs(fdata[l]['r_z'] - float(dic_fence[x]['initial_coordinates_z'])) < 0.5:
                                            xlist = [float(dic_fence[x]['initial_coordinates_x']),
                                                     float(dic_fence[x]['termination_coordinates_x'])]
                                            ylist = [float(dic_fence[x]['initial_coordinates_y']),
                                                     float(dic_fence[x]['termination_coordinates_y'])]
                                            xlist.sort()
                                            ylist.sort()
                                            if fdata[l]['r_x'] >= xlist[0] and \
                                                    fdata[l]['r_x'] <= xlist[1] and \
                                                    fdata[l]['r_y'] <= ylist[1] and \
                                                    fdata[l]['r_y'] >= ylist[0]:

                                                dict1["name"] = fdata[l]['device_id']
                                                dict1["warn_id"] = fdata[l]['username']
                                                dict1["warn_x"] = fdata[l]['x']
                                                dict1["warn_y"] = fdata[l]['y']
                                                timeArray = time.localtime(float(fdata[l]['created_on']))
                                                dict1["alarm_time"] = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
                                                if b_d:
                                                    if b_d[0]["alarm_level"] is not None:
                                                        dict1["alarm_level"] = b_d[0]["alarm_level"]
                                                    else:
                                                        dict1["alarm_level"] = "very_serious"
                                                dict1["type"] = 'electronic_fence'
                                    if dict1:
                                        list1.append(dict1)
                            elif efw_pbi:
                                # print("3721")
                                for y in efw_pbi:
                                    ename = FlaskAPI.get_e_name(table="prisoner_manager", data=y["prison_black_id"]) # 犯人白名单
                                    a2.append(ename[0]["name"])

                                for i in fdata.keys():
                                    dict1 = {}
                                    if i not in a2:
                                        if abs(fdata[i]['r_z'] - float(dic_fence[x]['initial_coordinates_z'])) < 0.5:
                                            xlist = [float(dic_fence[x]['initial_coordinates_x']),
                                                     float(dic_fence[x]['termination_coordinates_x'])]
                                            ylist = [float(dic_fence[x]['initial_coordinates_y']),
                                                     float(dic_fence[x]['termination_coordinates_y'])]
                                            xlist.sort()
                                            ylist.sort()
                                            if fdata[i]['r_x'] >= xlist[0] and \
                                                    fdata[i]['r_x'] <= xlist[1] and \
                                                    fdata[i]['r_y'] <= ylist[1] and \
                                                    fdata[i]['r_y'] >= ylist[0]:

                                                dict1["name"] = fdata[i]['device_id']
                                                dict1["warn_id"] = fdata[i]['username']
                                                dict1["warn_x"] = fdata[i]['x']
                                                dict1["warn_y"] = fdata[i]['y']
                                                timeArray = time.localtime(float(fdata[i]['created_on']))
                                                dict1["alarm_time"] = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
                                                if b_d:
                                                    if b_d[0]["alarm_level"] is not None:
                                                        dict1["alarm_level"] = b_d[0]["alarm_level"]
                                                    else:
                                                        dict1["alarm_level"] = "very_serious"
                                                dict1["type"] = 'electronic_fence'
                                    if dict1:
                                        list1.append(dict1)
                            # print(pefb_pbi, 'ddddd')
                            if pefb_pbi:
                                for z in pefb_pbi:
                                    ename1 = FlaskAPI.get_e_name1(table="prison_work_person",
                                                                 data=z["prison_black_id"])  # 狱警黑名单
                                    # print("cccccc", ename1)
                                    if ename1:
                                        a3.append(ename1[0]["name"])
                                        # print(a3)
                                    for l in a3:
                                        dict1 = {}
                                        if l in ydata.keys():
                                            if abs(ydata[l]['r_z'] - float(dic_fence[x]['initial_coordinates_z'])) < 0.5:
                                                xlist = [float(dic_fence[x]['initial_coordinates_x']),
                                                         float(dic_fence[x]['termination_coordinates_x'])]
                                                ylist = [float(dic_fence[x]['initial_coordinates_y']),
                                                         float(dic_fence[x]['termination_coordinates_y'])]
                                                xlist.sort()
                                                ylist.sort()
                                                if ydata[l]['r_x'] >= xlist[0] and \
                                                        ydata[l]['r_x'] <= xlist[1] and \
                                                        ydata[l]['r_y'] <= ylist[1] and \
                                                        ydata[l]['r_y'] >= ylist[0]:

                                                    dict1["name"] = ydata[l]['device_id']
                                                    dict1["warn_id"] = ydata[l]['username']
                                                    dict1["warn_x"] = ydata[l]['x']
                                                    dict1["warn_y"] = ydata[l]['y']
                                                    timeArray = time.localtime(float(ydata[l]['created_on']))
                                                    dict1["alarm_time"] = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
                                                    if b_d:
                                                        if b_d[0]["alarm_level"] is not None:
                                                            dict1["alarm_level"] = b_d[0]["alarm_level"]
                                                        else:
                                                            dict1["alarm_level"] = "very_serious"
                                                    dict1["type"] = 'electronic_fence'
                                        if dict1:
                                            list1.append(dict1)
                            elif pefw_pbi:
                                for z in pefw_pbi:
                                    ename = FlaskAPI.get_e_name1(table="prison_work_person", data=z["prison_black_id"]) # 犯人白名单
                                    # print("aa制", ename)
                                    if ename:
                                        a4.append(ename[0]["name"])
                                    # print('a4', a4)
                                    for l in ydata.keys():
                                        dicts1 = {}
                                        # print('ydata_l', l)
                                        if l not in a4:
                                            # print('qqqq', l)
                                            if abs(ydata[l]['r_z'] - float(dic_fence[x]['initial_coordinates_z'])) < 0.5:
                                                xlist = [float(dic_fence[x]['initial_coordinates_x']), float(dic_fence[x]['termination_coordinates_x'])]
                                                ylist = [float(dic_fence[x]['initial_coordinates_y']), float(dic_fence[x]['termination_coordinates_y'])]
                                                xlist.sort()
                                                ylist.sort()
                                                # print(xlist, ylist)
                                                # print('z<o.5', l)
                                                if ydata[l]['r_x'] >= xlist[0] and \
                                                        ydata[l]['r_x'] <= xlist[1] and \
                                                        ydata[l]['r_y'] <= ylist[1] and \
                                                        ydata[l]['r_y'] >= ylist[0]:
                                                    # print('wwwww', l)
                                                    dicts1["name"] = ydata[l]['device_id']
                                                    dicts1["warn_id"] = ydata[l]['username']
                                                    dicts1["warn_x"] = ydata[l]['x']
                                                    dicts1["warn_y"] = ydata[l]['y']
                                                    timeArray = time.localtime(float(ydata[l]['created_on']))
                                                    dicts1["alarm_time"] = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
                                                    if b_d:
                                                        if b_d[0]["alarm_level"] is not None:
                                                            dicts1["alarm_level"] = b_d[0]["alarm_level"]
                                                        else:
                                                            dicts1["alarm_level"] = "very_serious"
                                                    dicts1["type"] = 'electronic_fence'
                                        if dicts1:
                                            list1.append(dicts1)
                    print("222", list1)
                    res1 = FlaskAPI.write(list1, 'prison_warn')
                    if res1 == 'error':
                        return dic

                # 线程3将数据存入redis
                def thread3():
                    app.config['SESSION_REDIS'].set('R_data', json.dumps(data))
                    # master.set('R_data', json.dumps(data))

                # 线程2将数据存入psql
                def thread2():
                    res2 = FlaskAPI.write(data, 'device_data')
                    if res2 == 'error':
                        return dic

                # 线程4将数据写入临时表 device_linshi
                def thread4():
                    FlaskAPI.truncate_datas('device_data_copy')
                    res = FlaskAPI.write(data, 'device_data_copy')
                    if res == 'error':
                        return dic
                th1 = threading.Thread(target=thread1)
                th2 = threading.Thread(target=thread2)
                th3 = threading.Thread(target=thread3)
                th4 = threading.Thread(target=thread4)
                th4.start()
                th3.start()
                th1.start()
                th2.start()
                over_time = time.time()
                last_time = over_time - begin_time
                dic["msg"] = u"插入成功"
                dic['success'] = "True"
                dic['usetime'] = last_time
                return dic
            else:
                return '数据类型错误'
        else:
            return dic


# TODO：向前台发送实时的设备信息
class Fun5(Resource):
    def get(self):
        try:
            data = json.loads(str(app.config['SESSION_REDIS'].get('R_data'), encoding="utf-8"))
            return data
        except TypeError:
            return 'error'


# TODO：查询当前时间间隔内的围栏信息
class Fun6(Resource):
    def get(self):
        now_time = time.time()
        ef_datas = FlaskAPI.read("electronic_fence")
        lis1 = []
        for i in ef_datas:
            i["creation_time"] = time.mktime(time.strptime("{0}".format(i['creation_time']), '%Y-%m-%d %H:%M:%S'))
            i["end_time"] = time.mktime(time.strptime("{0}".format(i['end_time']), '%Y-%m-%d %H:%M:%S'))
            # 修正时差八小时
            i['creation_time'] += 60 * 60 * 8
            i['end_time'] += 60 * 60 * 8
            if i["creation_time"] <= now_time and i["end_time"] >= now_time:
                lis1.append(i)
        return lis1
    def post(self):
        data = request.json
        print(data)
        data = data[0]["name"]
        print(data)
        page = req.args['page']
        res = FlaskAPI.realtimes_fence_query(data)
        for i in res:
            print(111, i['creation_time'])
            i["creation_time"] = time.mktime(time.strptime("{0}".format(i['creation_time']), '%Y-%m-%d %H:%M:%S'))
            print(222, i['creation_time'])
            print(333, i['end_time'])
            i["end_time"] = time.mktime(time.strptime("{0}".format(i['end_time']), '%Y-%m-%d %H:%M:%S'))
            print(444, i['end_time'])
            if i["creation_time"] <= now_time and i["end_time"] >= now_time:
                lis1.append(i)
        if len(lis1) != 0:
            i = int(page) * 10
            j = (int(page) + 1) * 10
            number = len(lis1)
            res = lis1[i:j]
            res[0]["number"] = number
        return res


# TODO：电子围栏插入接口
class Fun7(Resource):
    def post(self):
        data = request.json
        dic = {}
        dic['code'] = 200
        dic["msg"] = u"请求错误！"
        dic["success"] = "false"
        begin_time = time.time()
        if data:
            # data[0]['creation_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data[0]['begin_time']))
            times = time.strftime('%Y%m%d%H%M%S', time.localtime(begin_time))
            print("111", times)
            data[0]['name'] = 'Fence' + str(int(times))

            now_time = time.time()
            print(now_time)
            # 日期转化时间戳
            data[0]['creation_time'] = time.mktime(time.strptime(data[0]['creation_time'], '%Y-%m-%d %H:%M:%S'))
            data[0]['end_time'] = time.mktime(time.strptime(data[0]['end_time'], '%Y-%m-%d %H:%M:%S'))
            # 修正时差八小时
            data[0]['creation_time'] -= 60*60*8
            data[0]['end_time'] -= 60*60*8
            # # # 判断电子围栏状态
            # if data[0]['creation_time'] < now_time:
            #     data[0]['state'] = '待进行'
            # elif data[0]['end_time'] > now_time:
            #     data[0]['state'] = '已失效'
            # else:
            #     data[0]['state'] = '进行中'
            # 时间戳转换日期
            data[0]['creation_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data[0]['creation_time']))
            data[0]['end_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data[0]['end_time']))
            print(data)
            res = FlaskAPI.write(data, 'electronic_fence')
            if res == 'error':
                print('error')
                return dic
            else:
                over_time = time.time()
                last_time = over_time - begin_time
                dic["msg"] = u"插入成功"
                dic['success'] = "True"
                dic['usetime'] = last_time
                return dic
        else:
            return dic

# TODO：据设备编号查询设备持有者的信息
class Fun8(Resource):
    def get(self):
        device_id = req.args['device_id']
        # print("2.14", device_id[0])
        if device_id[0] == "H":
            # device_id = eval(device_id)
            r = FlaskAPI.read(table='equipment_bracelet', target_field=['id'], condition="name={0}".format("'" + device_id + "'"))
            if r:
                res = FlaskAPI.read('prisoner_manager', target_field=['number'],
                                                            condition='bracelet_id={0}'.format(r[0]["id"]))
                if res:
                    res = {'username': r[0]['id'], 'ptype': '犯人', 'model_url': 'null'}
                else:
                    res = {'username': 'null', 'ptype': 'null', 'model_url': 'null'}
            else:
                res = FlaskAPI.read('prison_migrantsclass', target_field=['name'],
                                            condition='bracelet_id={0}'.format("'" + device_id + "'"))
                if res:
                    res = {'username': res[0]['name'], 'ptype': '外来人员', 'model_url': 'null'}
                else:
                    res = {'username': 'null', 'ptype': 'null', 'model_url': 'null'}
        elif device_id[0] == "X":
            # device_id = eval(device_id)
            r = FlaskAPI.read(table='equipment_chest_card', target_field=['id'],
                              condition="name={0}".format("'" + device_id + "'"))
            if r:
                res = FlaskAPI.read(table='prison_work_person', target_field=['work_men_id'],
                                    condition="chest_card_id={0}".format(r[0]["id"]))
                if res:
                    res = {'username': res[0]['work_men_id'], 'ptype': '狱警', 'model_url': 'null'}
                else:
                    res = {'username': 'null', 'ptype': 'null', 'model_url': 'null'}
            else:
                res = {'username': 'null', 'ptype': 'null', 'model_url': 'null'}


            # if not r:
            #     res = {'username': 'null', 'ptype': 'null', 'model_url': 'null'}
            # else:
            #     res = FlaskAPI.read('prisoner_manager', target_field=['number'],
            #                         condition='bracelet_id={0}'.format(r[0]["id"]))
            #     if not res:
            #         res = FlaskAPI.read('prison_migrantsclass', target_field=['name'],
            #                             condition='bracelet_id={0}'.format(r[0]["id"]))
            #         res = {'username': res[0]['name'], 'ptype': '外来人员', 'model_url': 'null'}
            #         if not res:
            #             res = {'username': 'null', 'ptype': 'null', 'model_url': 'null'}
            #     else:
            #         res = {'username': res[0]['number'], 'ptype': '犯人', 'model_url': 'null'}
        # d_type = int(req.args['type']) # 1-> 手环 2->胸牌
        # if d_type == 2:
        #     # res = FlaskAPI.read('equipment_bracelet', condition='name={0}'.format("'"+device_id+"'"))
        #     res = FlaskAPI.read('prison_work_person', target_field=['user_employee'],
        #                         condition='bracelet_id={0}'.format("'" + device_id + "'"))
        #     if res:
        #         res = {'username': res[0]['user_employee'], 'ptype': '狱警', 'model_url': 'null'}
        # elif d_type == 1:
        #     res = FlaskAPI.read('prisoner_manager', target_field=['number'],
        #                         condition='bracelet_id={0}'.format("'" + device_id + "'"))
        #     if not res:
        #         res = FlaskAPI.read('prison_migrantsclass', target_field=['name'],
        #                             condition='bracelet_id={0}'.format("'" + device_id + "'"))
        #         res = {'username': res[0]['name'], 'ptype': '外来人员', 'model_url': 'null'}
        #     else:
        #         res = {'username': res[0]['number'], 'ptype': '犯人', 'model_url': 'null'}
        else:
            res = {'username': 'null', 'ptype': 'null', 'model_url': 'null'}
        return res
# TODO：据设备id查询设备持有者的信息
# class Fun8(Resource):
#     def get(self):
#         device_id = request.args.get('device_id')
#         res = FlaskAPI.read('prison_equipment', target_field=['id', 'ptype', 'type'], condition='name={0}'.format("'"+device_id+"'"))
#         data = {}
#         # 警务人员
#         if res[0]['ptype'] == 1:
#             # 手环
#             if res[0]["type"] == 1:
#                 res = FlaskAPI.read('prison_work_person', target_field=['name', 'ptype'],
#                                     condition='bracelet_id={0}'.format(res[0]['id']))
#                 data["username"] = res[0]["name"]
#                 data["ptype"] = res[0]['ptype']
#             # 胸牌
#             elif res[0]["type"] == 2:
#                 res = FlaskAPI.read('prison_work_person', target_field=['name', 'ptype'],
#                                     condition='chest_card_id={0}'.format(res[0]['id']))
#                 data["username"] = res[0]["name"]
#                 data["ptype"] = res[0]['ptype']
#             else:
#                 res = {'username': 'null', 'ptype': 'null'}
#         # 犯人
#         elif res[0]['ptype'] == 2:
#             # 手环
#             if res[0]["type"] == 1:
#                 res = FlaskAPI.read('prisoner_manager', target_field=['number'],
#                                     condition='bracelet_id={0}'.format(res[0]['id']))
#                 data["username"] = res[0]["number"]
#                 data["ptype"] = 2
#             # 胸牌
#             elif res[0]["type"] == 2:
#                 res = FlaskAPI.read('prisoner_manager', target_field=['number'],
#                                     condition='chest_card_id={0}'.format(res[0]['id']))
#                 data["username"] = res[0]["number"]
#                 data["ptype"] = 2
#             else:
#                 res = {'username': 'null', 'ptype': 'null'}
#         # 外来人员
#         elif res[0]['ptype'] == 3:
#             # 手环
#             if res[0]["type"] == 1:
#                 res = FlaskAPI.read('prison_migrantsclass', target_field=['name', 'ptype'],
#                                     condition='bracelet_id={0}'.format(res[0]['id']))
#                 data["username"] = res[0]["name"]
#                 data["ptype"] = res[0]["ptype"]
#             # 胸牌
#             elif res[0]["type"] == 2:
#                 res = FlaskAPI.read('prison_migrantsclass', target_field=['name', 'ptype'],
#                                     condition='chest_card_id={0}'.format(res[0]['id']))
#                 data["username"] = res[0]["name"]
#                 data["ptype"] = res[0]["ptype"]
#             else:
#                 data = {'username': 'null', 'ptype': 'null'}
#         else:
#             data = {'username': 'null', 'ptype': 'null'}
#         return data


# TODO：根据建筑名称查询建筑信息
class Fun9(Resource):
    def get(self):
        name = request.args['name']
        # print(name)
        # type = int(eval(request.args['type']))
        # if type == 1:
        data = FlaskAPI.read('prison_building',
                             target_field=['id', 'name', 'building_x', 'building_y', 'building_z'],
                             condition="name='{0}'".format(name))
        if not data:
            return '建筑不存在'
        else:
            return data

# TODO: 根据建筑查房间、楼道
class Func1(Resource):
    def get(self):
        name = request.args["name"]
        # print(name)
        data1 = FlaskAPI.query_room_floor(name)
        # lis1 = []
        # lis2 = []
        dic = {}
        # dict1 = {}
        # dict11 = {}
        # dict2 = {}
        # list1 = []  # 房间坐标
        # for i in data1:
        #
        #     dict1["房间id"] = i["id"]
        #     dict1["房间名称"] = i["name"]
        #     dict2["房间坐标x"] = i["room_x"]
        #     dict2["房间坐标y"] = i["room_y"]
        #     dict2["房间坐标z"] = i["room_z"]
        #     list1.append(dict2)
        #     dict1["房间坐标"] = list1
        #     lis1.append(dict1)
        #     print("xxx", lis1)
        data2 = FlaskAPI.query_corridor_floor(name)
        # dict3 = {}
        # list2 = []  # 楼道坐标
        # for j in data2:
        #     dict11["楼道id"] = j["id"]
        #     dict11["楼道名称"] = j["name"]
        #     dict3["楼道坐标x"] = j["corridor_x"]
        #     dict3["楼道坐标y"] = j["corridor_y"]
        #     dict3["楼道坐标z"] = j["corridor_z"]
        #     list2.append(dict3)
        #     dict11["楼道坐标"] = list2
        #     lis2.append(dict11)
        dic["建筑名称"] = name
        dic["相关房间"] = data1
        dic["相关楼道"] = data2
        # elif type == 2:
        #     data = FlaskAPI.read('prison_boundary',
        #                   target_field=['id', 'name', 'boundary_start_x', 'boundary_start_y', 'boundary_start_x',
        #                                 'boundary_end_x', 'boundary_end_y', 'boundary_end_z'],
        #                   condition='name={0}'.format("'" + name + "'"))
        #     if not data:
        #         return '建筑不存在'
        # elif type == 3:
        #     data = FlaskAPI.read('prison.corridor',target_field=['id', 'name', 'room_x','room_y','room_z'],
        #                          condition='name={0}'.format("'" + name + "'"))
        #     if not data:
        #         return '建筑不存在'
        # else:
        #     return 'error'

        return dic


# TODO: 测试用例 Random
class Test1(Resource):
    def get(self):
        res = [{
            'id': 'a',
            'vname': 'obj1',
            'type': 'Thing',
            'name': 'Tom',
            'url': 'http://model.3dmomoda.com/models/954F58D2A3BD47149882482D5046ABF2/0/gltf/',
            'position': [random.uniform(315, 213), 0, random.uniform(23, -50)],
            'angle': 15,
        }, {
            'id': 'b',
            'vname': 'obj2',
            'type': 'Thing',
            'name': 'Jack',
            'url': 'http://model.3dmomoda.com/models/954F58D2A3BD47149882482D5046ABF2/0/gltf/',
            'position': [random.uniform(315, 213), 0, random.uniform(23, -50)],
            'angle': 0,
        }, {
            'id': 'c',
            'vname': 'obj3',
            'type': 'Thing',
            'name': 'Lisa',
            'url': 'http://model.3dmomoda.com/models/954F58D2A3BD47149882482D5046ABF2/0/gltf/',
            'position':  [random.uniform(315, 213), 0, random.uniform(23, -50)],
            'angle': 0,
        }]
        return res


# TODO：设备更新
class Dupdate(Resource):
    def post(self): # type 1-> 门禁 2-> 摄像头 3-> 基站 4->车禁 5->一键报警
        # data = request.json
        # set1 = set()
        # list1 = []
        # number = 0
        # for i in data:
        #     number += 1
        #     # res = FlaskAPI.read(target_field=["id"], table='prison_equipment_type', condition="name='{0}'".format(i['type']))
        #     # if res:
        #     i['type'] = res[0]['id']
        #     i['name'] = 'equipment' + str(int(time.time())) + str(number)
        #     i['resource_id'] = 11
        #     list1.append(i)
        #     if i['type'] == '1':
        #         FlaskAPI.write(table='equipment_access_control', data=list1)
        #     # else:
        #         set1.add(i['type'])
        # res1 = FlaskAPI.write(table='prison_equipment', data=list1)
        # return {'res': list(set1)}
        data = request.json
        # print("测试", data)
        m_list = []
        s_list = []
        j_list = []
        c_list = []
        y_list = []
        for i in data:
            if i['type'] == '1':
                i.pop("type")
                m_list.append(i)
            elif i['type'] == '2':
                i.pop("type")
                s_list.append(i)
                print(s_list)
            elif i['type'] == '3':
                i.pop("type")
                j_list.append(i)
            elif i['type'] == '4':
                i.pop("type")
                c_list.append(i)
            elif i['type'] == '5':
                i.pop("type")
                y_list.append(i)
            else:
                pass
        if m_list is not None:
            FlaskAPI.rinse_insert(table='equipment_access_control', data=m_list)
        if s_list is not None:
            FlaskAPI.rinse_insert(table='equipment_camera', data=s_list)
        if j_list is not None:
            FlaskAPI.rinse_insert(table='equipment_base_station', data=j_list)
        if c_list is not None:
            FlaskAPI.rinse_insert(table='equipment_vehicle_ban', data=c_list)
        if y_list is not None:
            FlaskAPI.rinse_insert(table='equipment_call_police', data=y_list)
        return {'res': 'update完成'}


# TODO: 拖拽设备
class Drag(Resource):
    def post(self): # type 1-> 门禁 2-> 摄像头 3-> 基站 4->车禁 5->一键报警
        data = request.json
        m_list = []
        s_list = []
        j_list = []
        c_list = []
        y_list = []
        number = 0
        for i in data:
            number += 1
            if i['type'] == '1':
                i['name'] = 'M' + str(int(time.time())) + str(number)
                i.pop("type")
                m_list.append(i)
            elif i['type'] == '2':
                i['name'] = 'S' + str(int(time.time())) + str(number)
                i.pop("type")
                s_list.append(i)
            elif i['type'] == '3':
                i['name'] = 'J' + str(int(time.time())) + str(number)
                i.pop("type")
                j_list.append(i)
            elif i['type'] == '4':
                i['name'] = 'L' + str(int(time.time())) + str(number)
                i.pop("type")
                c_list.append(i)
            elif i['type'] == '5':
                i['name'] = 'Y' + str(int(time.time())) + str(number)
                i.pop("type")
                y_list.append(i)
            else:
                pass
        if m_list is not None:
            FlaskAPI.write(table='equipment_access_control', data=m_list)
        if s_list is not None:
            FlaskAPI.write(table='equipment_camera', data=s_list)
        if j_list is not None:
            FlaskAPI.write(table='equipment_base_station', data=j_list)
        if c_list is not None:
            FlaskAPI.write(table='equipment_car', data=c_list)
        if y_list is not None:
            FlaskAPI.write(table='equipment_call_police', data=y_list)
        return {'res': '拖拽完成'}




# TODO: 边界告警
class Alarm_border(Resource):
    def get(self):
        res = FlaskAPI.read('prison_alarm_rule', target_field=["alarm_level", "alarm_range"], condition="name='边界'")
        if res == 'error':
            return '失败', 200


# TODO: 建筑信息查询接口
class Query_build(Resource):
    def get(self):
        res = FlaskAPI.read('prison_building')
        if res == 'error':
            return '失败', 200
        else:
            res = [{'id': i['id'], 'name': i['name'], 'building_x': i['building_x'], 'building_y': i['building_y'],
                    'building_z': i['building_z'], 'if_coordinate': i['if_coordinate'], 'coordinate_name':
                        i['coordinate_name'], 'building_long': i['building_long'], 'building_wide':
                        i['building_wide'], 'building_high': i['building_high']} for i in res]
            return res, 200




# TODO：房间信息查询接口
class Query_room(Resource):
    def get(self):
        res = FlaskAPI.read('prison_room')
        if res == 'error':
            return '失败', 200
        else:
            res = [{'id': i['id'], 'room_building': i['room_building'], 'name': i['name'], 'room_x': i['room_x'], 'room_y': i['room_y'],
                    'room_z': i['room_z'], 'if_coordinate': i['if_coordinate'], 'coordinate_name':
                        i['coordinate_name'], 'room_long': i['room_long'], 'room_wide':
                        i['room_wide'], 'room_high': i['room_high']} for i in res]
            return res, 200


# TODO：边界信息查询接口
class Query_boundary(Resource):
    def get(self):
        res = FlaskAPI.read('prison_boundary')
        if res == 'error':
            return '失败', 200
        else:
            res = [{'id': i['id'], 'name': i['name'], 'boundary_start_x': i['boundary_start_x'],
                    'boundary_start_y': i['boundary_start_y'], 'boundary_start_z': i['boundary_start_z'],
                    'boundary_end_x': i['boundary_end_x'], 'boundary_end_y': i['boundary_end_y'], 'boundary_end_z':
                        i['boundary_end_z'], 'boundary_high': i['boundary_high']} for i in res]
            return res, 200


# TODO：视角插入接口
class Insert_visual_angle(Resource):
    def post(self):
        data = request.json
        dic = {}
        dic['code'] = 200
        dic["msg"] = u"请求错误！"
        dic["success"] = "false"
        begin_time = time.time()
        if data:
            res = FlaskAPI.write(data, 'visual_angle')
            if res == 'error':
                # print('error')
                return dic
            else:
                over_time = time.time()
                last_time = over_time - begin_time
                dic["msg"] = u"插入成功"
                dic['success'] = "True"
                dic['usetime'] = last_time
                return dic
        else:
            return dic


# TODO：视角查询接口
class Query_visual_angle(Resource):
    def post(self):
        data = request.json
        print(333, data)
        res = FlaskAPI.read(table='visual_angle', condition="create_person="+str(data[0]["create_person"]))
        if res == 'error':
            return '失败', 200
        else:
            return res, 200

# TODO: 楼道信息插入
class InsertCorridorInfo(Resource):
    def post(self):
        data = request.json
        # print(123, data)
        dic = {}
        dic['code'] = 200
        dic["msg"] = u"请求错误！"
        dic["success"] = "false"
        begin_time = time.time()
        if data:
            for i in data:
                b_id = FlaskAPI.read(table='prison_building', target_field=['id'], condition="name='{0}'".format(i['corridor_building']))
                i["corridor_building"] = b_id[0]['id']
            res = FlaskAPI.rinse_insert(data, table='prison_corridor')
            if res == 'error':
                return dic
            else:
                over_time = time.time()
                last_time = over_time - begin_time
                dic["msg"] = u"插入成功"
                dic['success'] = "True"
                dic['usetime'] = last_time
                return dic
        else:
            return dic


# TODO: 房间信息插入
class InsertRoomInfo(Resource):
    def post(self):
        data = request.json
        dic = {}
        dic['code'] = 200
        dic["msg"] = u"请求错误！"
        dic["success"] = "false"
        begin_time = time.time()
        if data:
            for i in data:
                b_id = FlaskAPI.read(table='prison_building', target_field=['id'], condition="name='{0}'".format(i['room_building']))
                i["room_building"] = b_id[0]['id']
            res = FlaskAPI.rinse_insert(data, table='prison_room')
            if res == 'error':
                return dic
            else:
                over_time = time.time()
                last_time = over_time - begin_time
                dic["msg"] = u"插入成功"
                dic['success'] = "True"
                dic['usetime'] = last_time
                return dic
        else:
            return dic



# TODO: 建筑信息插入
class InsertBuildingInfo(Resource):
    def post(self):
        data = request.json
        # print("buiding", data)
        dic = {}
        dic['code'] = 200
        dic["msg"] = u"请求错误！"
        dic["success"] = "false"
        begin_time = time.time()
        if data:
            res = FlaskAPI.rinse_insert(data, table='prison_building')
            if res == 'error':
                return dic
            else:
                over_time = time.time()
                last_time = over_time - begin_time
                dic["msg"] = u"插入成功"
                dic['success'] = "True"
                dic['usetime'] = last_time
                return dic
        else:
            return dic

# TODO: 设备列表接口
class QueryDevice(Resource):
    def get(self):
        type = int(eval(request.args['type']))
        if type == 1: # 基站
            data = FlaskAPI.read('equipment_base_station')
            if not data:
                return '基站不存在'
        elif type == 2: # 门禁
            data = FlaskAPI.read('equipment_access_control')
            if not data:
                return '门禁不存在'
        elif type == 3: # 车禁
            data = FlaskAPI.read('equipment_vehicle_ban')
            if not data:
                return '车禁不存在'
        elif type == 4: # 周界
            data = FlaskAPI.read('equipment_perimeter')
            if not data:
                return '周界不存在'
        elif type == 5: # 摄像头
            data = FlaskAPI.read('equipment_camera')
            if not data:
                return '摄像头不存在'
        elif type == 6: # 一键报警
            data = FlaskAPI.read('equipment_call_police')
            if not data:
                return '一键报警不存在'
        elif type == 7: # 车载摄像头
            data = FlaskAPI.read('equipment_car_camera')
            if not data:
                return '车载摄像头不存在'
        elif type == 8: # 胸牌
            data = FlaskAPI.read('equipment_chest_card')
            if not data:
                return '胸牌不存在'
        elif type == 9: # 手环
            data = FlaskAPI.read('equipment_bracelet')
            if not data:
                return '手环不存在'
        elif type == 10: # 车辆
            data = FlaskAPI.read('equipment_car')
            if not data:
                return '车辆不存在'
        else:
            return '设备类型error'
        return data

class QueryGroup(Resource):
    def get(self):
        res = FlaskAPI.read('prison_following_group', target_field=['id', 'name', 'starting_position', 'end_position',
                                                                    'boss_eq', 'approver_person', 'state', 'reason'])
        if res == 'error':
            return '失败', 200
        else:
            return res, 200


# TODO: 人员列表接口
class QueryPerson(Resource):
    def post(self):
        data = request.json
        # print("++++++++++++++++++")
        if data[0]["ptype"] == 1: # yujing
            res = FlaskAPI.read('prison_work_person')
            for i in res:
                i['Date_of_birth'] = str(i['Date_of_birth'])
                i['entry_time'] = str(i['entry_time'])
                # 将日期转换成时间戳
                i["create_date"] = time.mktime(time.strptime(i['create_date'], '%Y-%m-%d %H:%M:%S'))
                i["write_date"] = time.mktime(time.strptime(i['write_date'], '%Y-%m-%d %H:%M:%S'))
                # 修正时差八小时
                i["create_date"] += 60*60*8
                i["write_date"] += 60 * 60 * 8
                # 将转换时间戳转换成日期格式
                i["create_date"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(i["create_date"]))
                i["write_date"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(i["write_date"]))
        elif data[0]["ptype"] == 2: # fanren
            res = FlaskAPI.read('prisoner_manager')
            for i in res:
                i['birthday'] = str(i['birthday'])
                i['imprisonment_time'] = str(i['imprisonment_time'])
                i['out_time'] = str(i['out_time'])
                # 将日期转换成时间戳
                i["create_date"] = time.mktime(time.strptime(i['create_date'], '%Y-%m-%d %H:%M:%S'))
                i["write_date"] = time.mktime(time.strptime(i['write_date'], '%Y-%m-%d %H:%M:%S'))
                # 修正时差八小时
                i["create_date"] += 60 * 60 * 8
                i["write_date"] += 60 * 60 * 8
                # 将转换时间戳转换成日期格式
                i["create_date"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(i["create_date"]))
                i["write_date"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(i["write_date"]))
        elif data[0]["ptype"] == 3: # wailairen
            res = FlaskAPI.read('prison_migrantsclass')
            for i in res:
                i['Date_of_birth'] = str(i['Date_of_birth'])
                i['access_object_start_time'] = str(i['access_object_start_time'])
                i['access_object_end_time'] = str(i['access_object_end_time'])
                # 将日期转换成时间戳
                i["create_date"] = time.mktime(time.strptime(i['create_date'], '%Y-%m-%d %H:%M:%S'))
                i["write_date"] = time.mktime(time.strptime(i['write_date'], '%Y-%m-%d %H:%M:%S'))
                # 修正时差八小时
                i["create_date"] += 60 * 60 * 8
                i["write_date"] += 60 * 60 * 8
                # 将转换时间戳转换成日期格式
                i["create_date"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(i["create_date"]))
                i["write_date"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(i["write_date"]))
        else:
            return 'error'
        return res


# TODO: 电子围栏列表接口
class QueryFence(Resource):
    def get(self):
        page = req.args['page']
        res = FlaskAPI.read('electronic_fence')
        if res == 'error':
            return '失败', 200
        else:
            for i in res:
                creation_time = i["creation_time"].strftime('%Y-%m-%d %H:%M:%S')
                i["creation_time"] = creation_time
                end_time = i["end_time"].strftime('%Y-%m-%d %H:%M:%S')
                i["end_time"] = end_time
            if len(res) != 0:
                i = int(page) * 10
                j = (int(page) + 1) * 10
                number = len(res)
                res = res[i:j]
                res[0]["number"] = number
            return res

    def post(self):
        data = request.json
        print(data)
        # if data[0]["name"] == '':
        #     return "该电子围栏不存在"
        # else:
        data = data[0]["name"]
        print(data)
        page = req.args['page']
        res = FlaskAPI.realtimes_fence_query(data)
        if len(res) != 0:
            i = int(page) * 10
            j = (int(page) + 1) * 10
            number = len(res)
            res = res[i:j]
            res[0]["number"] = number
        return res


# TODO: 插入实时数据查询接口
class QueryDeviceData(Resource):
    def get(self):
        res = FlaskAPI.read('device_data')
        if res == 'error':
            return '失败', 200
        else:
            return res, 200


# TODO: 查询所有信息
class QueryPrisonRoom(Resource):
    def get(self):
    # SQL 查询语句
        res = FlaskAPI.query_data()
        if res == 'error':
            return '失败', 200
        else:
            return res, 200


# TODO: 门禁刷卡信息插入接口
class MData(Resource):
    def post(self):
        m_data = request.json
        dic = {}
        dic['code'] = 200
        dic["msg"] = u"请求错误！"
        dic["success"] = "false"
        begin_time = time.time()
        if m_data and type(m_data) == list:
            res2 = FlaskAPI.punchCard_data_insert(m_data)
            if res2 == 'error':
                return dic
            over_time = time.time()
            last_time = over_time - begin_time
            dic["msg"] = u"插入成功"
            dic['success'] = "True"
            dic['usetime'] = last_time
            return dic
        else:
            return dic


# TODO: 车禁刷卡信息插入接口
class CarData(Resource):
    def post(self):
        m_data = request.json
        dic = {}
        dic['code'] = 200
        dic["msg"] = u"请求错误！"
        dic["success"] = "false"
        begin_time = time.time()
        if m_data and type(m_data) == list:
            res2 = FlaskAPI.bstate_car_insert(m_data)
            if res2 == 'error':
                return dic
            over_time = time.time()
            last_time = over_time - begin_time
            dic["msg"] = u"插入成功"
            dic['success'] = "True"
            dic['usetime'] = last_time
            return dic
        else:
            return dic


# TODO: 报警信息插入接口
class BData(Resource):
    def post(self):
        m_data = request.json
        dic = {}
        dic['code'] = 200
        dic["msg"] = u"请求错误！"
        dic["success"] = "false"
        begin_time = time.time()
        if m_data and type(m_data) == list:
            FlaskAPI.truncate_datas('historical_alarm_copy')
            res1 = FlaskAPI.write(m_data, 'historical_alarm_copy')
            res2 = FlaskAPI.bstate_data_insert(m_data)
            if res2 == 'error' or res1 == 'error':
                return dic
            over_time = time.time()
            last_time = over_time - begin_time
            dic["msg"] = u"插入成功"
            dic['success'] = "True"
            dic['usetime'] = last_time
            return dic
        else:
            return dic


# TODO: 静态设备实时状态信息插入接口
class StaticData(Resource):
    def post(self):
        s_data = request.json
        dic = {}
        dic['code'] = 200
        dic["msg"] = u"请求错误！"
        dic["success"] = "false"
        begin_time = time.time()
        if s_data and type(s_data) == list:
            for i in s_data:
                if i["name"].startswith('M'):
                    # print("hhh", i)
                    FlaskAPI.state_data_update(table='equipment_access_control', data=i)
                elif i['name'].startswith('C'):
                    FlaskAPI.state_data_update(table='equipment_vehicle_ban', data=i)
                elif i['name'].startswith('Z'):
                    FlaskAPI.state_data_update(table='equipment_perimeter', data=i)
                elif i['name'].startswith('Y'):
                    FlaskAPI.state_data_update(table='equipment_call_police', data=i)
                elif i['name'].startswith('S'):
                    FlaskAPI.state_data_update(table='equipment_camera', data=i)
                elif i['name'].startswith('J'):
                    FlaskAPI.state_data_update(table='equipment_base_station', data=i)
                else:
                    pass
            FlaskAPI.truncate_datas('state_table_copy')
            res1 = FlaskAPI.write(s_data, 'state_table_copy')
            res2 = FlaskAPI.state_data_insert(s_data)
            if res2 == 'error' or res1 == 'error':
                return dic
            over_time = time.time()
            last_time = over_time - begin_time
            dic["msg"] = u"插入成功"
            dic['success'] = "True"
            dic['usetime'] = last_time
            return dic
        else:
            return dic


@app.route('/')
def hello():
    return 'hello world'


# TODO: 胸牌历史记录页面
@app.route('/search/device/<device_id>', methods=['GET'])
def fun(device_id):
    # session['username'] = 'aaa'
    url = request.path
    name = url.split('/')[3]

    return render_template('show_info.html', device_id=name)


# TODO: 胸牌/手环历史记录
@app.route('/show_info', methods=['post'])
def fun1():
    device_id = req.form.get('device_id')
    # print(device_id)
    start_time = req.form.get('start_time')
    # print(start_time)
    over_time = req.form.get("over_time")

    start_time = time.mktime(time.strptime(start_time, '%Y-%m-%d %H:%M:%S'))
    over_time = time.mktime(time.strptime(over_time, '%Y-%m-%d %H:%M:%S'))
    print("111", start_time)
    print("222", over_time)
    res = FlaskAPI.getequiptment(device_id, start_time, over_time)
    # print("xxxxx", res)
    if res == '空' or not res:
        return jsonify({'message': '未查询到结果!'})
    else:
        lis1 = []
        for i in res:
            result = []
            print("111", i["created_on"])
            timeArray = time.localtime(i["created_on"])
            co = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
            result.append(i["device_id"])
            result.append(i["product"])
            result.append(i["signal_intensity"])
            result.append(i["motion_state"])
            result.append(i["battery_quantity"])
            result.append(i["heart_beat"])
            result.append(i["pulse"])
            result.append(i["warning"])
            result.append(i["ref_things"])
            result.append(i["ref_x"])
            result.append(i["ref_y"])
            result.append(i["ref_z"])
            result.append(i["building"])
            result.append(i["floor"])
            result.append(i["room"])
            result.append(i["ptype"])
            result.append(i["username"])
            result.append(i["model_url"])
            result.append(i["x"])
            result.append(i["y"])
            result.append(i["z"])
            result.append(i["longitude"])
            result.append(i["latitude"])
            result.append(i["position_reliability"])
            result.append(i["state"])
            result.append(co)
            lis1.append(result)
        return jsonify(lis1)


# TODO：手环历史记录页面
@app.route('/search/prison/<device_id>', methods=['GET'])
def prison(device_id):
    url = request.path
    name = url.split('/')[3]
    return render_template('prison.html', device_id=name)


# TODO：车辆历史记录页面
@app.route('/search/car/<device_id>', methods=['GET'])
def car(device_id):
    url = request.path
    name = url.split('/')[3]
    return render_template('foreign.html', device_id=name)


# TODO：基站记录信息
@app.route('/search/base_station/<device_id>', methods=['GET'])
def basestation(device_id):
    url = request.path
    name = url.split('/')[3]
    return render_template('show1.html', device_id=name)


# TODO: 基站记录
@app.route('/show_infos', methods=['post'])
def prison1():
    device_id = req.form.get('device_id')
    # print(device_id)
    # device_id1 = req.form.get('device_id1')
    # print(device_id1)
    start_time = req.form.get('start_time')
    # print(start_time)
    over_time = req.form.get("over_time")
    # print(over_time)
    res = FlaskAPI.search_psql(start_time, over_time, device_id)

    if res == '' or res == 'error' or not res:
        return jsonify({'message': '未查询到结果!'})
    else:
        lis1 = []
        for i in res:
            result = []
            timeArray = time.localtime(i["time"])
            co = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
            result.append(i["name"])
            result.append(co)
            result.append(i["state"])
            lis1.append(result)
        # print(type(lis1))
        return jsonify(lis1)


# TODO: 刷卡记录
@app.route('/show_record', methods=['post'])
def record():
    device_id = req.form.get('device_id')
    # print(device_id)
    # device_id1 = req.form.get('device_id1')
    # print(device_id1)
    start_time = req.form.get('start_time')
    # print(start_time)
    over_time = req.form.get("over_time")
    # print(over_time)
    res = FlaskAPI.search_fsql(start_time, over_time, device_id)
    if res == '' or res == 'error' or not res:
        return jsonify({'message': '未查询到结果!'})
    else:
        lis1 = []
        for i in res:
            result = []
            username = FlaskAPI.query_name(i["guard_id"])
            if len(username) == 0:
                username = 'Ps:(人员姓名不匹配，请核对)'
            timeArray = time.localtime(i["time"])
            co = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
            result.append(i["name"])
            result.append(i["guard_id"])
            result.append(username)
            result.append(co)
            result.append(i["action"])
            lis1.append(result)
        # print(type(lis1))
        return jsonify(lis1)


# TODO: 车辆记录
@app.route('/car_record', methods=['post'])
def carrecord():
    device_id = req.form.get('device_id')
    # print(device_id)
    # device_id1 = req.form.get('device_id1')
    # print(device_id1)
    start_time = req.form.get('start_time')
    # print(start_time)
    over_time = req.form.get("over_time")
    # print(over_time)
    res = FlaskAPI.search_csql(start_time, over_time, device_id)
    if res == '' or res == 'error' or not res:
        return jsonify({'message': '未查询到结果!'})
    else:
        lis1 = []
        for i in res:

            result = []
            timeArray = time.localtime(i["time"])
            co = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
            result.append(i["name"])
            result.append(co)
            result.append(i["action"])
            lis1.append(result)
        print(type(lis1))
        return jsonify(lis1)


# TODO: 周界/一键报警记录
@app.route('/zj_record', methods=['post'])
def zjrecord():
    device_id = req.form.get('device_id')
    # print(device_id)
    # device_id1 = req.form.get('device_id1')
    # print(device_id1)
    start_time = req.form.get('start_time')
    # print(start_time)
    over_time = req.form.get("over_time")
    # print(over_time)
    res = FlaskAPI.search_hsql(start_time, over_time, device_id)
    if res == '' or res == 'error' or not res:
        return jsonify({'message': '未查询到结果!'})
    else:
        lis1 = []
        for i in res:
            result = []
            timeArray = time.localtime(i["time"])
            co = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
            result.append(i["name"])
            result.append(co)
            result.append(i["type"])
            result.append(i["x"])
            result.append(i["y"])
            result.append(i["z"])
            lis1.append(result)
        print(type(lis1))
        return jsonify(lis1)


# TODO：门禁记录信息
@app.route('/search/entrance_quard/<device_id>', methods=['GET'])
def eguard(device_id):
    url = request.path
    name = url.split('/')[3]
    return render_template('show2.html', device_id=device_id)


# TODO：车禁记录信息
@app.route('/search/car_ban/<device_id>', methods=['GET'])
def carban(device_id):
    url = request.path
    name = url.split('/')[3]
    return render_template('show3.html', device_id=name)


# TODO：周界记录信息
@app.route('/search/perimeter/<device_id>', methods=['GET'])
def perimeter(device_id):
    url = request.path
    name = url.split('/')[3]
    return render_template('show4.html', device_id=name)


# TODO：摄像头记录信息
@app.route('/search/camera/<device_id>', methods=['GET'])
def camera(device_id):
    url = request.path
    name = url.split('/')[3]
    return render_template('show5.html', device_id=name)


# TODO：一件报警记录信息
@app.route('/search/akeyalarm/<device_id>', methods=['GET'])
def akeyalarm(device_id):
    url = request.path
    name = url.split('/')[3]
    return render_template('show6.html', device_id=name)


# TODO：车载摄像头记录信息
@app.route('/search/carcamera/<device_id>', methods=['GET'])
def carcamera(device_id):
    url = request.path
    name = url.split('/')[3]
    return render_template('show7.html', device_id=name)


# TODO: 门禁刷卡记录
@app.route('/record/door/<device_id>', methods=['GET'])
def door(device_id):
    url = request.path
    name = url.split('/')[3]
    print(name)
    return render_template('record1.html', device_id=name)


# TODO: 车禁刷卡记录
@app.route('/record/car/<device_id>', methods=['GET'])
def cars(device_id):
    url = request.path
    name = url.split('/')[3]
    return render_template('record2.html', device_id=name)


# TODO: 周界历史报警
@app.route('/record/zj/<device_id>', methods=['GET'])
def zj(device_id):
    url = request.path
    name = url.split('/')[3]
    return render_template('record3.html', device_id=name)


# TODO: 一键报警
@app.route('/record/yjbj/<device_id>', methods=['GET'])
def yjbj(device_id):
    url = request.path
    name = url.split('/')[3]
    return render_template('record4.html', device_id=name)



# TODO：获取信息并返回人员信息
class Imginfo(Resource):
    def post(self):
        m_data = request.json
        print(m_data)
        dic = {}
        # dic['code'] = 200
        # dic["msg"] = u"请求错误！"
        # dic["success"] = "false"
        # begin_time = time.time()
        if m_data and type(m_data) == list:
            # res2 = FlaskAPI.bstate_data_insert(m_data)
            # if res2 == 'error':
            for i in m_data:

            #     return dic
                data = i["device_id"]
                print(data)
                res = FlaskAPI.search_person_info(data)
                # over_time = time.time()
                # last_time = over_time - begin_time
                # dic["msg"] = u"插入成功"
                # dic['success'] = "True"
                # dic['usetime'] = last_time
            return res
        else:
            return dic


# TODO：轨迹信息
class Guiji(Resource):
    def post(self):
        data = request.json
        print("xxx", data)
        if data and type(data) == list:
            for i in data:
                device_id = i["device_id"]
                print(device_id)
                create_time = i["create_time"]
                end_time = i["end_time"]
                t1 = time.strptime(create_time, "%Y-%m-%d %H:%M:%S")
                create_time = time.mktime(t1)
                print(create_time)
                t2 = time.strptime(end_time, "%Y-%m-%d %H:%M:%S")
                end_time = time.mktime(t2)
                print(end_time)
                res = FlaskAPI.getguiji(device_id, create_time, end_time)
                return res
        else:
            return "数据格式错误"


# TODO: 建筑》楼层》房间人员数量统计
class BuildingNumber(Resource):
    def get(self):
        # 查询所有建筑名称
        lis1 = []
        all_building = FlaskAPI.query_allbuilding()
        print('222', lis1)
        res3 = FlaskAPI.query_person_floorss()
        for i in all_building:
            dic1 = {}
            res1 = FlaskAPI.query_person_building(data=i["name"])
            dic1["name"] = i["name"]
            dic1['number'] = res1[0]["count"]
            dic1["id"] = i["id"]
            # 根据建筑名称查询房间列表
            res2 = FlaskAPI.query_room_list(data=i["id"])
            lis2 = []
            for j in res2:
                dic2 = {}
                res2 = FlaskAPI.query_person_room(j["name"])
                dic2["name"] = j["name"]
                dic2["number"] = res2[0]["count"]
                dic2["id"] = j["id"]
                lis2.append(dic2)
            dic1["room"] = lis2
            # # 根据建筑名称查询楼道列表
            lis3 = []
            for z in res3:
                dic3 = {}
                # print(z["building"], i["name"])
                if z["building"] == i["name"]:
                    dic3["name"] = z["floor"]
                    dic3["number"] = z["count"]
                    dic3["id"] = z["id"]
                    lis3.append(dic3)
            dic1["floor"] = lis3
            lis1.append(dic1)
        # dic4 = {}
        # dic4["name"] = '空地'
        # res2 = FlaskAPI.query_person_building(data='')
        # dic4["number"] = res2
        # dic4["room"] = []

        # lis1.append(dic4)

        return lis1


# TODO: 建筑》楼层》房间人员数量统计 ps:1
class BuildingNumber1(Resource):
    def get(self):
        # 查询所有建筑名称
        lis1 = []
        all_building = FlaskAPI.query_allbuilding()



        res3 = FlaskAPI.query_person_floorss()
        for i in all_building:
            dic1 = {}
            res1 = FlaskAPI.query_person_building(data=i["name"])
            dic1["name"] = i["name"]
            dic1['number'] = res1[0]["count"]
            dic1["id"] = i["id"]
            # 根据建筑名称查询房间列表
            res2 = FlaskAPI.query_room_list(data=i["id"])
            lis2 = []
            for j in res2:
                dic2 = {}
                res2 = FlaskAPI.query_person_room(data1=j["name"], data2=i["name"])
                dic2["name"] = j["name"]
                dic2["number"] = res2[0]["count"]
                dic2["id"] = j["id"]
                lis2.append(dic2)
            dic1["room"] = lis2
            # # # 根据建筑名称查询楼道列表
            # lis3 = []
            # for z in res3:
            #     dic3 = {}
            #     # print(z["building"], i["name"])
            #     if z["building"] == i["name"]:
            #         dic3["name"] = z["floor"]
            #         dic3["number"] = z["count"]
            #         dic3["id"] = z["id"]
            #         lis3.append(dic3)
            # dic1["floor"] = lis3
            lis1.append(dic1)
        res2 = FlaskAPI.query_person_building_nul()
        print("111", res2)
        dic4 = {}
        dic4["name"] = '空地'
        dic4["number"] = res2[0]["count"]
        dic4["room"] = []
        lis1.append(dic4)
        return lis1


# TODO: 建筑》楼层》房间设备数量统计 ps:1
class DeviceNumber1(Resource):
    def get(self):
        # 查询所有建筑名称
        all_building = FlaskAPI.query_allbuilding()
        lis1 = []
        # res3 = FlaskAPI.query_person_floorss()
        building_res = 0
        for i in all_building:
            dic1 = {}
            res1 = FlaskAPI.device_building_query_id(data1='equipment_camera', data2=i["id"]) # 摄像头
            res2 = FlaskAPI.device_building_query_id(data1='equipment_access_control', data2=i["id"]) # 门禁
            res3 = FlaskAPI.device_building_query_id(data1='equipment_perimeter', data2=i["id"])  # 周界
            res4 = FlaskAPI.device_building_query_id(data1='equipment_call_police', data2=i["id"])  # 一键报警
            res5 = FlaskAPI.device_building_query_id(data1='equipment_base_station', data2=i["id"])  # 基站
            res6 = FlaskAPI.device_building_query_id(data1='equipment_vehicle_ban', data2=i["id"])  # 车禁
            res = int(res1[0]["count"]) + int(res2[0]["count"]) + int(res3[0]["count"]) + int(res4[0]["count"]) + int(res5[0]["count"]) + int(res6[0]["count"])
            print(res)
            building_res += res
            # res1 = FlaskAPI.query_person_building(data=i["name"])
            dic1["name"] = i["name"]
            dic1['number'] = res
            dic1["id"] = i["id"]
            # 根据建筑名称查询房间列表
            res2 = FlaskAPI.query_room_list(data=i["id"])
            lis2 = []
            for j in res2:
                dic2 = {}
                res1 = FlaskAPI.device_room_query_id(data1='equipment_camera', data2=i["id"], data3=j["id"])  # 摄像头
                res2 = FlaskAPI.device_room_query_id(data1='equipment_access_control', data2=i["id"], data3=j["id"])  # 门禁
                res3 = FlaskAPI.device_room_query_id(data1='equipment_perimeter', data2=i["id"], data3=j["id"])  # 周界
                res4 = FlaskAPI.device_room_query_id(data1='equipment_call_police', data2=i["id"], data3=j["id"])  # 一键报警
                res5 = FlaskAPI.device_room_query_id(data1='equipment_base_station', data2=i["id"], data3=j["id"])  # 基站
                res6 = FlaskAPI.device_room_query_id(data1='equipment_vehicle_ban', data2=i["id"], data3=j["id"])  # 车禁
                # res2 = FlaskAPI.device_room_query_id(data1=j["name"], data2=i["name"])
                res = int(res1[0]["count"]) + int(res2[0]["count"]) + int(res3[0]["count"]) + int(
                    res4[0]["count"]) + int(res5[0]["count"]) + int(res6[0]["count"])
                dic2["name"] = j["name"]
                dic2["number"] = res
                dic2["id"] = j["id"]
                lis2.append(dic2)
            dic1["room"] = lis2
            # # # 根据建筑名称查询楼道列表
            # lis3 = []
            # for z in res3:
            #     dic3 = {}
            #     # print(z["building"], i["name"])
            #     if z["building"] == i["name"]:
            #         dic3["name"] = z["floor"]
            #         dic3["number"] = z["count"]
            #         dic3["id"] = z["id"]
            #         lis3.append(dic3)
            # dic1["floor"] = lis3
            lis1.append(dic1)
        dic3 = {}
        res1 = FlaskAPI.query_null(data1='equipment_camera')  # 摄像头
        res2 = FlaskAPI.query_null(data1='equipment_access_control')  # 门禁
        res3 = FlaskAPI.query_null(data1='equipment_perimeter')  # 周界
        res4 = FlaskAPI.query_null(data1='equipment_call_police')  # 一键报警
        res5 = FlaskAPI.query_null(data1='equipment_base_station')  # 基站
        res6 = FlaskAPI.query_null(data1='equipment_vehicle_ban')  # 车禁
        res = int(res1[0]["count"]) + int(res2[0]["count"]) + int(res3[0]["count"]) + int(
            res4[0]["count"]) + int(res5[0]["count"]) + int(res6[0]["count"])
        dic3["name"] = '空地'
        dic3["number"] = res-building_res
        dic3["room"] = []
        lis1.append(dic3)
        return lis1


# TODO: 实时数据人员数量统计
class PersonNumQuery(Resource):
    def get(self):
        # 狱警
        data = '1'
        p1 = FlaskAPI.query_person_number(data)
        lis1 = []
        dic1 = {}
        dic1['name'] = '狱警'
        dic1['number'] = p1
        dic1["type"] = "1"
        lis1.append(dic1)
        # 犯人
        data = '2'
        p2 = FlaskAPI.query_person_number(data)
        dic2 = {}
        dic2['name'] = '犯人'
        dic2['number'] = p2
        dic2["type"] = "2"
        lis1.append(dic2)
        #  外来人员
        data = '3'
        p3 = FlaskAPI.query_person_number(data)
        dic3 = {}
        dic3['name'] = '外来人员'
        dic3['number'] = p3
        dic3["type"] = "3"
        lis1.append(dic3)
        return lis1


# TODO: 根据人员类型查询人员详细名单
class PersonListQuery(Resource):
    def post(self):
        type = request.json
        print(type)
        if type[0]['type'] == "1":
            res1 = FlaskAPI.query_person_details(1)
        elif type[0]['type'] == "2":
            res1 = FlaskAPI.query_person_details(2)
        elif type[0]['type'] == "3":
            res1 = FlaskAPI.query_person_details(3)
        else:
            res1 = '类型错误'
        return res1


# 3D界面点击人员名称
class PersonInfoQuery_3D(Resource):
    def post(self):
        # 获取点击的时间及人员可标识属性
        data = request.json
        # 根据点击时间获取该时间下的所有人员信息
        time = data[0]["time"]
        res = FlaskAPI.person_list_query()
        lis = []
        for i in res:
            if data[0]["id"] == i["device_id"]:
                dic = {}
                return i


# 实时数据人员类型 编号 类别查询接口
class RealtimeInfoQuery(Resource):
    def get(self):
        res = FlaskAPI.realtime_info_query()
        return res

    def post(self):
        page = req.args['page']
        data = request.json
        data = data[0]["name"]
        res = FlaskAPI.realtimes_info_query(data)
        if len(res) != 0:
            i = int(page) * 10
            j = (int(page) + 1) * 10
            number = len(res)
            res = res[i:j]
            res[0]["number"] = number
        return res


# TODO：定位
class RealtimeAllInfo(Resource):
    def post(self):
        # page = req.args['page']
        data = request.json
        res = FlaskAPI.realtime_allinfo(d2=data[0]["username"])
        # print("xxx", res)
        # # 狱警
        # if data[0]["ptype"] == '1':
        #     res = FlaskAPI.realtime_allinfo1(d2=data[0]["username"])
        # elif data[0]["ptype"] == '2':
        #     res = FlaskAPI.realtime_allinfo2(d2=data[0]["username"])
        # elif data[0]["ptype"] == '3':
        #     res = FlaskAPI.realtime_allinfo3(d2=data[0]["username"])
        # else:
        # #     res = "人员类型错误"
        # if len(res) != 0:
        #     i = int(page) * 10
        #     j = (int(page) + 1) * 10
        #     number = len(res)
        #     res = res[i:j]
        #     res[0]["number"] = number
        return res


# 查询人员接口
class RealtimePerson(Resource):
    def get(self):
        data = req.args['page']
        print(data)
        res1 = FlaskAPI.qpwp()
        # print(res1)
        for i in res1:
            if i["chest_card_id"] is not None:
                device_id = FlaskAPI.query_device_id(i["chest_card_id"])
                device_id = device_id[0]["name"]
                # print(device_id)
            else:
                device_id = ''
                # print(device_id)
            i["chest_card_id"] = device_id
        res2 = FlaskAPI.qpm()
        for j in res2:
            if j["bracelet_id"] is not None:
                device_id = FlaskAPI.query_device_id1(j["bracelet_id"])
                device_id = device_id[0]["name"]
                # print(device_id)
            else:
                device_id = ''
                # print(device_id)
            j["bracelet_id"] = device_id
        res3 = FlaskAPI.qpms()
        for z in res3:
            if z["bracelet_id"] is not None:
                device_id = FlaskAPI.query_device_id1(z["bracelet_id"])
                device_id = device_id[0]["name"]
                # print(device_id)
            else:
                device_id = ''
                # print(device_id)
            z["bracelet_id"] = device_id
        res = res1 + res2 + res3
        number = len(res)
        i = int(data) * 10
        j = (int(data) + 1) * 10
        res = res[i:j]
        res[0]["number"] = number
        return res


# 查询设备接口
class RealtimeDeviceNum(Resource):
    def get(self):
        data = req.args['page']
        print(data)
        query_data = FlaskAPI.querystates()
        print(query_data)
        lis1_name = []
        dic = {}
        # lis1_state = []
        for i in query_data:
            lis1_name.append(i["name"])
            dic[i['name']] = i['state']
            # lis1_state.append(i["state"])
        # print(query_data)
        res1 = FlaskAPI.qebs()
        for i in res1:
            if i["name"] in lis1_name:
                # res_state = FlaskAPI.querystateone(i["name"])
                # i["state"] = res_state[0]["state"]
                i["state"] = dic[i["name"]]
            else:
                i["state"] = ''
        res2 = FlaskAPI.qeac()
        for i in res2:
            if i["name"] in lis1_name:
                # res_state = FlaskAPI.querystateone(i["name"])
                # i["state"] = res_state[0]["state"]
                i["state"] = dic[i["name"]]
            else:
                i["state"] = ''
        res3 = FlaskAPI.qevb()
        for i in res3:
            if i["name"] in lis1_name:
                # res_state = FlaskAPI.querystateone(i["name"])
                # i["state"] = res_state[0]["state"]
                i["state"] = dic[i["name"]]
            else:
                i["state"] = ''
        res4 = FlaskAPI.qp()
        for i in res4:
            if i["name"] in lis1_name:
                # res_state = FlaskAPI.querystateone(i["name"])
                # i["state"] = res_state[0]["state"]
                i["state"] = dic[i["name"]]
            else:
                i["state"] = ''
        res5 = FlaskAPI.qc()
        for i in res5:
            if i["name"] in lis1_name:
                # res_state = FlaskAPI.querystateone(i["name"])
                # i["state"] = res_state[0]["state"]
                i["state"] = dic[i["name"]]
            else:
                i["state"] = ''
        res6 = FlaskAPI.qecp()
        for i in res6:
            if i["name"] in lis1_name:
                # res_state = FlaskAPI.querystateone(i["name"])
                # i["state"] = res_state[0]["state"]
                i["state"] = dic[i["name"]]
            else:
                i["state"] = ''
        res7 = FlaskAPI.qecc()
        for i in res7:
            if i["name"] in lis1_name:
                # res_state = FlaskAPI.querystateone(i["name"])
                # i["state"] = res_state[0]["state"]
                i["state"] = dic[i["name"]]
            else:
                i["state"] = ''
        res8 = FlaskAPI.qecca()
        for i in res8:
            if i["name"] in lis1_name:
                # res_state = FlaskAPI.querystateone(i["name"])
                # i["state"] = res_state[0]["state"]
                i["state"] = dic[i["name"]]
            else:
                i["state"] = ''
        res9 = FlaskAPI.qeba()
        for i in res9:
            if i["name"] in lis1_name:
                # res_state = FlaskAPI.querystateone(i["name"])
                # i["state"] = res_state[0]["state"]
                i["state"] = dic[i["name"]]
            else:
                i["state"] = ''
        res10 = FlaskAPI.qeca()
        for i in res10:
            if i["name"] in lis1_name:
                # res_state = FlaskAPI.querystateone(i["name"])
                # i["state"] = res_state[0]["state"]
                i["state"] = dic[i["name"]]
            else:
                i["state"] = ''
        res = res1 + res2 + res3 + res4 + res5 + res6 + res7 + res8 + res9 + res10
        number = len(res)
        i = int(data) * 10
        j = (int(data) + 1) * 10
        res = res[i:j]
        res[0]["number"] = number
        return res

# 设备搜索
class RealtimeDeviceQuery(Resource):
    def post(self):
        data = request.json
        # if data[0]["name"] == '':
        #     return "该设备不存在"
        # else:
        data = data[0]["name"]
        page = req.args['page']
        # res = FlaskAPI.realtimes_device_query(data)
        query_data = FlaskAPI.querystates()
        ls= []
        dic = {}
        for i in query_data:
            ls.append(i['name'])
            dic[i['name']] = i['state']
        #     基站
        res1 = FlaskAPI.sbAll(1, 'equipment_base_station', data)
        for i in res1:
            if i['name'] in ls:
                i['state'] = dic[i['name']]

        #     门禁
        res2 = FlaskAPI.sbAll(2, 'equipment_access_control', data)
        for i in res2:
            if i['name'] in ls:
                i['state'] = dic[i['name']]

        #     车禁
        res3 = FlaskAPI.sbAll(3, 'equipment_vehicle_ban', data)
        for i in res3:
            if i['name'] in ls:
                i['state'] = dic[i['name']]

        #     周界
        res4 = FlaskAPI.sbAll(4, 'equipment_perimeter', data)
        for i in res4:
            if i['name'] in ls:
                i['state'] = dic[i['name']]

        #     摄像头
        res5 = FlaskAPI.sbAll(5, 'equipment_camera', data)
        for i in res5:
            if i['name'] in ls:
                i['state'] = dic[i['name']]

        #     一键报警
        res6 = FlaskAPI.sbAll(6, 'equipment_call_police', data)
        for i in res6:
            if i['name'] in ls:
                i['state'] = dic[i['name']]

        #     车载摄像头
        res7 = FlaskAPI.sbAll(7, 'equipment_car_camera', data)
        for i in res7:
            if i['name'] in ls:
                i['state'] = dic[i['name']]

        #     胸脯
        res8 = FlaskAPI.sbAll(8, 'equipment_chest_card', data)
        for i in res8:
            if i['name'] in ls:
                i['state'] = dic[i['name']]
        #     手环
        res9 = FlaskAPI.sbAll(9, 'equipment_bracelet', data)
        for i in res9:
            if i['name'] in ls:
                i['state'] = dic[i['name']]

        #     车辆
        res10 = FlaskAPI.sbAll(10, 'equipment_car', data)
        for i in res10:
            if i['name'] in ls:
                i['state'] = dic[i['name']]

        res = res1 + res2 + res3 +res4 +res5 +res6 + res7 +res8 + res9 +res10
        if len(res) != 0:
            i = int(page) * 10
            j = (int(page) + 1) * 10
            number = len(res)
            res = res[i:j]
            res[0]["number"] = number
        return res

# TODO: 实时数据设备数量统计
class DeviceNumQuery(Resource):
    def get(self):
        # 基站
        data = 'J'
        p1 = FlaskAPI.query_device_number(data)
        lis1 = []
        dic1 = {}
        dic1['name'] = '基站'
        dic1['number'] = p1
        dic1["type"] = "J"
        lis1.append(dic1)
        # 门禁
        data = 'M'
        p2 = FlaskAPI.query_device_number(data)
        dic2 = {}
        dic2['name'] = '门禁'
        dic2['number'] = p2
        dic2["type"] = "M"
        lis1.append(dic2)
        #  车禁
        data = 'C'
        p3 = FlaskAPI.query_device_number(data)
        dic3 = {}
        dic3['name'] = '车禁'
        dic3['number'] = p3
        dic3["type"] = "C"
        lis1.append(dic3)
        #  周界
        data = 'Z'
        p4 = FlaskAPI.query_device_number(data)
        dic4 = {}
        dic4['name'] = '周界'
        dic4['number'] = p4
        dic4["type"] = "Z"
        lis1.append(dic4)
        #  摄像头
        data = 'S'
        p5 = FlaskAPI.query_device_number(data)
        dic5 = {}
        dic5['name'] = '摄像头'
        dic5['number'] = p5
        dic5["type"] = "S"
        lis1.append(dic5)
        #  一键报警
        data = 'Y'
        p6 = FlaskAPI.query_device_number(data)
        dic6 = {}
        dic6['name'] = '一键报警'
        dic6['number'] = p6
        dic6["type"] = "Y"
        lis1.append(dic6)
        #  胸牌
        data = 'X'
        p8 = FlaskAPI.query_device_number(data)
        dic8 = {}
        dic8['name'] = '胸牌'
        dic8['number'] = p8
        dic8["type"] = "X"
        lis1.append(dic8)
        #  手环
        data = 'H'
        p9 = FlaskAPI.query_device_number(data)
        dic9 = {}
        dic9['name'] = '手环'
        dic9['number'] = p9
        dic9["type"] = "H"
        lis1.append(dic9)
        #  车辆
        data = 'L'
        p10 = FlaskAPI.query_device_number(data)
        dic10 = {}
        dic10['name'] = '车辆'
        dic10['number'] = p10
        dic10["type"] = "L"
        lis1.append(dic10)
        #  车载摄像头
        data = 'CZ'
        p7 = FlaskAPI.query_device_allnumber()
        print(111, p1)
        p7 = int(p7[0]["count"]) - int(p1[0]["count"]) - int(p2[0]["count"]) - int(p3[0]["count"]) - int(p4[0]["count"]) - \
             int(p5[0]["count"]) - int(p6[0]["count"]) - int(p8[0]["count"]) - int(p9[0]["count"]) - int(p10[0]["count"])
        dic7 = {}
        dic7['name'] = '车载摄像头'
        dic7['number'] = p7
        dic7["type"] = "CZ"
        lis1.append(dic7)
        return lis1


# TODO: 实时数据设备数量统计
class ERPDeviceNumQuery(Resource):
    def get(self):
        # 基站
        p1 = FlaskAPI.query_devicetab_numbers(table='equipment_base_station')
        lis1 = []
        dic1 = {}
        dic1['name'] = '基站'
        dic1['number'] = p1[0]["count"]
        lis1.append(dic1)
        # 门禁
        p2 = FlaskAPI.query_devicetab_numbers(table='equipment_access_control')
        dic2 = {}
        dic2['name'] = '门禁'
        dic2['number'] = p2[0]["count"]
        lis1.append(dic2)
        #  车禁
        p3 = FlaskAPI.query_devicetab_numbers(table='equipment_vehicle_ban')
        dic3 = {}
        dic3['name'] = '车禁'
        dic3['number'] = p3[0]["count"]
        lis1.append(dic3)
        #  周界
        p4 = FlaskAPI.query_devicetab_numbers(table='equipment_perimeter')
        dic4 = {}
        dic4['name'] = '周界'
        dic4['number'] = p4[0]["count"]
        lis1.append(dic4)
        #  摄像头
        p5 = FlaskAPI.query_devicetab_numbers(table='equipment_camera')
        dic5 = {}
        dic5['name'] = '摄像头'
        dic5['number'] = p5[0]["count"]
        lis1.append(dic5)
        #  一键报警
        p6 = FlaskAPI.query_devicetab_numbers(table='equipment_call_police')
        dic6 = {}
        dic6['name'] = '一键报警'
        dic6['number'] = p6[0]["count"]
        lis1.append(dic6)
        #  胸牌
        p8 = FlaskAPI.query_devicetab_numbers(table='equipment_chest_card')
        dic8 = {}
        dic8['name'] = '胸牌'
        dic8['number'] = p8[0]["count"]
        lis1.append(dic8)
        #  手环
        p9 = FlaskAPI.query_devicetab_numbers(table='equipment_bracelet')
        dic9 = {}
        dic9['name'] = '手环'
        dic9['number'] = p9[0]["count"]
        lis1.append(dic9)
        #  车辆
        p10 = FlaskAPI.query_devicetab_numbers(table='equipment_car')
        dic10 = {}
        dic10['name'] = '车辆'
        dic10['number'] = p10[0]["count"]
        lis1.append(dic10)
        #  车载摄像头
        p7 = FlaskAPI.query_devicetab_numbers(table='equipment_car_camera')
        dic7 = {}
        dic7['name'] = '车载摄像头'
        dic7['number'] = p7[0]["count"]
        lis1.append(dic7)
        return lis1


 # TODO: 实时数据设备报警统计
class DeviceAlarmQuery(Resource):
    def get(self):
        data = req.args['page']
        res = FlaskAPI.query_device_alarm()
        i = int(data) * 10
        j = (int(data) + 1) * 10
        number = len(res)
        res = res[i:j]
        res[0]["number"] = number
        return res


# # TODO: 告警搜索接口
# class Fence_inits(Resource):
#     def get(self):
#         data = request.json
#         # if data[0]["name"] == '':
#         #     return "该人员不存在"
#         # else:
#         data1 = data[0]["name"]
#         # 获取页数
#         data = req.args['page']
#         i = int(data) * 10
#         # # 获取当前时间时间戳
#         # now_time = time.strftime("%Y-%m-%d %H:%M:%S")
#         # print(now_time)
#         # 查询数量
#         number = FlaskAPI.realtimes_deviceinfo_query_numbers(data)
#         res = FlaskAPI.realtimes_deviceinfo_query(data1, i)
#         res[0]['number'] = number
#         # 查询所有电子围栏
#         # 遍历电子围栏
#         return res

class RealtimeDeviceinfoQuery(Resource):
    def get(self):
        data = req.args['page']
        data = int(data) * 10
        res = FlaskAPI.realtimes_deviceinfo_list(data)
        num = FlaskAPI.history_counts()
        if len(res) != 0:
            res[0]['number'] = num[0]['count']
        return res
    def post(self):
        data = request.json
        print(data)
        # if data[0]["name"] == '':
        #     return "该人员不存在"
        # else:
        data = data[0]["name"]
        print(data)
        page = req.args['page']
        res = FlaskAPI.realtimes_deviceinfo_query(data)
        if len(res) != 0:
            i = int(page) * 10
            j = (int(page) + 1) * 10
            number = len(res)
            res = res[i:j]
            res[0]["number"] = number
        return res



# 搜索电子围栏初始化接口
class Fence_init(Resource):
    def get(self):
        # 获取页数
        data = req.args['page']
        # 获取当前时间时间戳
        now_time = time.time()
        # 查询所有电子围栏
        ef_datas = FlaskAPI.read("electronic_fence")
        lis1 = []
        # 遍历电子围栏
        for i in ef_datas:
            # 日期格式化时间戳
            i["creation_time"] = time.mktime(time.strptime("{0}".format(i['creation_time']), '%Y-%m-%d %H:%M:%S'))
            i["end_time"] = time.mktime(time.strptime("{0}".format(i['end_time']), '%Y-%m-%d %H:%M:%S'))
            if i["creation_time"] <= now_time and i["end_time"] >= now_time:
                lis1.append(i)
        number = len(lis1)
        i = int(data) * 10
        j = (int(data) + 1) * 10
        res = lis1[i:j]
        res[0]["number"] = number
        return res


# 热力图统计楼层人、楼层人数及x,y,z坐标
class HeatingPower(Resource):
    def get(self):
        # 查询所有建筑名称
        all_building = FlaskAPI.query_chart_allbuilding()
        lis1 = []
        # res3 = FlaskAPI.query_person_floorss()
        for i in all_building:
            dic1 = {}
            res1 = FlaskAPI.query_chart_building(data=i["name"])
            dic1["name"] = i["name"]
            dic1['number'] = res1[0]["count"]
            dic1["x"] = i["building_x"]
            dic1["y"] = i["building_y"]
            dic1["z"] = i["building_z"]
            dic1["long"] = i["building_long"]
            dic1["wide"] = i["building_wide"]
            lis1.append(dic1)
        return lis1

# 跟随组3D
class Followgroup(Resource):
    def get(self):
        # 查询跟随组
        lis1 = []
        res1 = FlaskAPI.query_follow_group_3D()
        for i in res1:
            dic1 = {}
            dic1["id"] = i["id"]
            dic1['groupname'] = i["name"] # {'跟随组名字': "123"}
            dic1['start_position'] = i["starting_position"]
            dic1['end_position'] = i["end_position"]
            res = FlaskAPI.query_workman_device_id(i['boss_eq'])
            dic1['device'] = res[0]["name"]
            # lis2 = []
            # 查狱警组
            res2 = FlaskAPI.query_follow_group_workman(i['id'])
            lis3 = []

            for j in res2:
                # dic2 = {}

                # 查狱警name, chest_card_id
                res3 = FlaskAPI.query_workman_info(j['group_id'])
                print(333, res3)
                for z in res3:
                    dic3 = {}
                    # 查狱警设备device_id
                    res4 = FlaskAPI.query_workman_device_id(z['chest_card_id'])
                    print(222, res4)
                    dic3["name"] = z['name']
                    print(111, res4[0]['name'])
                    dic3['device'] = res4[0]['name']
                    # dic3[z['name']] = res4[0]['name']
                    lis3.append(dic3)
            dic1['workman'] = lis3
                # lis2.append(dic2)
            # 查犯人组
            res22 = FlaskAPI.query_follow_group_prison(i['id'])
            lis33 = []

            for j in res22:
                # dic22 = {}

                # 查狱警name, chest_card_id
                res33 = FlaskAPI.query_prison_info((j['group_id']))

                for z in res33:
                    dic33 = {}
                    # 查狱警设备device_id
                    res44 = FlaskAPI.query_prison_device_id(z['bracelet_id'])

                    dic33["name"] = z['name']
                    dic33["device"] = res44[0]['name']
                    lis33.append(dic33)
            dic1['prison'] = lis33
                # lis2.append(dic22)
            lis1.append(dic1)
        return lis1


class FollowgroupAll(Resource):
    def get(self):
        # 查询跟随组
        data = req.args['page']
        data = int(data) * 10
        lis1 = []
        res1 = FlaskAPI.query_follow_group_all(data)
        for i in res1:
            dic1 = {}
            dic1['state'] = i["state"]
            dic1['groupname'] = i["name"] # {'跟随组名字': "123"}
            dic1['start_position'] = i["starting_position"]
            dic1['end_position'] = i["end_position"]
            res = FlaskAPI.query_workman_device_id(i['boss_eq'])
            dic1['device'] = res[0]["name"]
            # lis2 = []
            # 查狱警组
            res2 = FlaskAPI.query_follow_group_workman(i['id'])
            lis3 = []

            for j in res2:
                # dic2 = {}

                # 查狱警name, chest_card_id
                res3 = FlaskAPI.query_workman_info(j['group_id'])
                print(333, res3)
                for z in res3:
                    dic3 = {}
                    # 查狱警设备device_id
                    res4 = FlaskAPI.query_workman_device_id(z['chest_card_id'])
                    print(222, res4)
                    dic3["name"] = z['name']
                    print(111, res4[0]['name'])
                    dic3['device'] = res4[0]['name']
                    # dic3[z['name']] = res4[0]['name']
                    lis3.append(dic3)
            dic1['workman'] = lis3
                # lis2.append(dic2)
            # 查犯人组
            res22 = FlaskAPI.query_follow_group_prison(i['id'])
            lis33 = []

            for j in res22:
                # dic22 = {}

                # 查狱警name, chest_card_id
                res33 = FlaskAPI.query_prison_info((j['group_id']))

                for z in res33:
                    dic33 = {}
                    # 查狱警设备device_id
                    res44 = FlaskAPI.query_prison_device_id(z['bracelet_id'])

                    dic33["name"] = z['name']
                    dic33["device"] = res44[0]['name']
                    lis33.append(dic33)
            dic1['prison'] = lis33
                # lis2.append(dic22)
            lis1.append(dic1)
        num = FlaskAPI.page_group_counts()
        if len(lis1) != 0:
            lis1[0]['number'] = num[0]['count']
        return lis1


# TODO: 获取当前日期电子围栏告警前十条，不满十条则全部获取
class FenceAlarm(Resource):
    def get(self):
        # res = time.strftime("%Y-%m-%d", time.localtime())
        # ten_fence = FlaskAPI.query_fence_alarm(res)
        # return ten_fence

        times = time.strftime("%Y-%m-%d", time.localtime())
        data = req.args['page']
        type = 'electronic_fence'
        res = FlaskAPI.followalarmtoday(data, type, times)
        num = FlaskAPI.page_fence_alarm_counts('electronic_fence', times)
        if len(res) != 0:
            res[0]['number'] = num[0]['count']
        return res


# TODO: 分页获取所有电子围栏告警的十条
class PageFenceAlarm(Resource):
    def get(self):
        data = req.args['page']
        data = int(data) * 10
        num = FlaskAPI.page_fence_alarm_count(data='electronic_fence')
        print(333444,  num[0]['count'])
        res = FlaskAPI.page_fence_alarm(data)
        print(44433, res)
        if len(res) != 0:
            res[0]['number'] = num[0]['count']
        return res


# TODO: 获取当前日期报警前十条，不满十条则全部获取
class AllAlarm(Resource):
    def get(self):
        res = time.strftime("%Y-%m-%d", time.localtime())
        # print(d2)
        # d2 = '2019-06-14'
        # d1 = datetime.datetime.now()
        # print(d1)
        # data = time.time()
        # data = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data))
        ten_fence = FlaskAPI.query_fence_alarms(res)
        # print(ten_fence)
        return ten_fence


# TODO: 分页获取所有报警的十条
class PageAllAlarm(Resource):
    def get(self):
        data = req.args['page']
        data = int(data) * 10
        number = FlaskAPI.page_fence_alarms_count()
        res = FlaskAPI.page_fence_alarms(data)
        res[0]['number'] = number[0]['count']
        return res


# TODO: historical_alarm_copy删除告警
class DelHisAlarm(Resource):
    def post(self):
        data = request.json
        FlaskAPI.delhisalarm(data[0]["device_id"])
        return 'ok'


# TODO: mark_name 插入接口
class MarkInsert(Resource):
    def post(self):
        data = request.json
        res = FlaskAPI.queryforname(data[0]['name'])
        if len(res) == 0:
            FlaskAPI.markinsert(data)
        else:
            return '已存在'
        return 'ok'

# TODO: mark_name 查看接口
class MarkQuery(Resource):
    def get(self):
        res = FlaskAPI.markquery("mark_name")
        return res

# TODO: mark_name 删除接口
class MarkDel(Resource):
    def post(self):
        data = request.json
        FlaskAPI.markdel(data[0]["name"])
        return 'ok'

# TODO: 获取跟随组组长device_id和x,y,z
class GetFollowGroup(Resource):
    def post(self):
        data = request.json
        print(data)
        res = FlaskAPI.queryidbydeviceid(data[0]["device_id"])
        print(res)
        resp = FlaskAPI.querystate((res[0]["id"]))
        if len(resp) == 0:
            return False
        else:
            return True

# TODO: 电子围栏 删除接口
class FenceDel(Resource):
    def post(self):
        data = request.json
        FlaskAPI.fencedel(data[0]["name"])
        return 'ok'


# TODO: 跟随组告警当前一天
class FollowAlarmToday(Resource):
    def get(self):
        times = time.strftime("%Y-%m-%d", time.localtime())
        data = req.args['page']
        data = int(data) * 10
        type = 'alarm_following_group'
        res = FlaskAPI.followalarmtoday(data, type, times)
        num = FlaskAPI.page_fence_alarm_counts('alarm_following_group', times)
        if len(res) != 0:
            res[0]['number'] = num[0]['count']
        return res

# TODO: 跟随组告警历史
class FollowAlarmHistory(Resource):
    def get(self):
        # times = time.strftime("%Y-%m-%d", time.localtime())
        data = req.args['page']
        data = int(data) * 10
        res = FlaskAPI.followalarmhistory(data)
        num = FlaskAPI.page_fence_alarm_count('person')
        if len(res) != 0:
            res[0]['number'] = num[0]['count']
        return res


# TODO: 边界告警当前一天
class BoundAlarmToday(Resource):
    def get(self):
        times = time.strftime("%Y-%m-%d", time.localtime())
        data = req.args['page']
        data = int(data) * 10
        type = 'alarm_boundary'
        res = FlaskAPI.followalarmtoday(data, type, times)
        num = FlaskAPI.page_fence_alarm_counts('alarm_boundary', times)
        if len(res) != 0:
            res[0]['number'] = num[0]['count']
        return res

# TODO: 硬件告警当前一天
class AbnormalAlarmToday(Resource):
    def get(self):
        times = time.strftime("%Y-%m-%d", time.localtime())
        data = req.args['page']
        data = int(data) * 10
        type = 'abnormal'
        res = FlaskAPI.followalarmtoday(data, type, times)
        num = FlaskAPI.page_fence_alarm_counts('abnormal', times)
        if len(res) != 0:
            res[0]['number'] = num[0]['count']
        return res

# TODO: 主动触发告警当前一天
class PersonAlarmToday(Resource):
    def get(self):
        times = time.strftime("%Y-%m-%d", time.localtime())
        data = req.args['page']
        type = 'person'
        res = FlaskAPI.followalarmtoday(data, type, times)
        num = FlaskAPI.page_fence_alarm_counts('person', times)
        if len(res) != 0:
            res[0]['number'] = num[0]['count']
        return res


# TODO: 当天告警
class HistoryAlarmToday(Resource):
    def get(self):
        res = FlaskAPI.realtimes_deviceinfo_lists()
        return res


# TODO：周边设备信息
class CircumDevice(Resource):
    def post(self):
        data = request.json
        print("xxx", data)
        if data and type(data) == list:
            for i in data:
                device_id = i["device_id"]
                print(device_id)
                create_time = i["create_time"]
                end_time = i["end_time"]
                t1 = time.strptime(create_time, "%Y-%m-%d %H:%M:%S")
                create_time = time.mktime(t1)
                print(create_time)
                t2 = time.strptime(end_time, "%Y-%m-%d %H:%M:%S")
                end_time = time.mktime(t2)
                print(end_time)
                res = FlaskAPI.getguiji(device_id, create_time, end_time)
                length = int(len(res))
                print(length)
                res = res[0:length:30]
            camera_lis1 = FlaskAPI.query_camera("equipment_camera") # 摄像头
            camera_lis2 = FlaskAPI.query_camera("equipment_base_station")  # 基站
            camera_lis3 = FlaskAPI.query_camera("equipment_access_control") # 门禁
            camera_lis4 = FlaskAPI.query_camera("equipment_vehicle_ban") # 车禁
            camera_lis5 = FlaskAPI.query_camera("equipment_call_police") # 一键报警
            lis1 = []
            for y in camera_lis1:
                # liss1 = []
                for x in res:
                    if math.sqrt((x["x"]-y["control_x"])**2+(x["y"]-y["control_y"])**2+(x["z"]-y["control_z"])**2) < 5:
                        # liss1.extend([, y["control_x"], y["control_y"], y["control_z"]])
                        # liss1.append()
                        lis1.append(y["name"])
            for y in camera_lis2:
                # liss2 = []
                for x in res:
                    if math.sqrt((x["x"]-y["control_x"])**2+(x["y"]-y["control_y"])**2+(x["z"]-y["control_z"])**2) < 5:
                        # liss2.extend([y["name"], y["control_x"], y["control_y"], y["control_z"]])
                        lis1.append(y["name"])
            for y in camera_lis3:
                # liss3 = []
                for x in res:
                    if math.sqrt((x["x"]-y["control_x"])**2+(x["y"]-y["control_y"])**2+(x["z"]-y["control_z"])**2) < 5:
                        # liss3.extend([y["name"], y["control_x"], y["control_y"], y["control_z"]])
                        lis1.append(y["name"])
            for y in camera_lis4:
                # liss4 = []
                for x in res:
                    if math.sqrt((x["x"]-y["control_x"])**2+(x["y"]-y["control_y"])**2+(x["z"]-y["control_z"])**2) < 5:
                        # liss4.extend([y["name"], y["control_x"], y["control_y"], y["control_z"]])
                        lis1.append(y["name"])
            for y in camera_lis5:
                # liss5 = []
                for x in res:
                    if math.sqrt((x["x"]-y["control_x"])**2+(x["y"]-y["control_y"])**2+(x["z"]-y["control_z"])**2) < 5:
                        # liss5.extend([y["name"], y["control_x"], y["control_y"], y["control_z"]])
                        lis1.append(y["name"])
            lis1 = list(set(lis1))
            return lis1
        else:
            return "数据格式错误"


# TODO: 当前各类型告警1-电子围栏2-跟随组3-剩下三个
class TodayAlarm(Resource):
    def get(self):
        times = time.strftime("%Y-%m-%d", time.localtime())
        type = request.args["type"]
        print(type)
        if type == '1':
            res = FlaskAPI.today_alarm("electronic_fence", times)
        elif type == '2':
            res = FlaskAPI.today_alarm("alarm_following_group", times)
        else:
            r1 = FlaskAPI.today_alarm("alarm_boundary", times)
            r2 = FlaskAPI.today_alarm("abnormal", times)
            r3 = FlaskAPI.today_alarm("person", times)
            res = r1+r2+r3
        return res

# TODO: 查询条件触发告警搜索
class ConditionAlarmFind(Resource):
    def post(self):
        data = request.json
        data = data[0]["name"]
        page = req.args['page']
        i = int(page) * 10
        res = FlaskAPI.conditionalarmfind(data, i)
        # if len(res) != 0:
        #         #     i = int(page) * 10
        #         #     j = (int(page) + 1) * 10
        #         #     number = len(res)
        #         #     res = res[i:j]
        result = FlaskAPI.conditionalarmfindnum(data)
        res[0]["number"] = result[0]["count"]
        return res

# TODO: 根据跟随组名称查询跟随组
class ConditionFollowFind(Resource):
    def post(self):
        data = request.json
        data1 = data[0]["name"]
        page = req.args['page']
        data = page * 10
        lis1 = []
        res1 = FlaskAPI.query_follow_group_by_name(data1, data)
        for i in res1:
            dic1 = {}
            dic1['state'] = i["state"]
            dic1['groupname'] = i["name"] # {'跟随组名字': "123"}
            dic1['start_position'] = i["starting_position"]
            dic1['end_position'] = i["end_position"]
            res = FlaskAPI.query_workman_device_id(i['boss_eq'])
            dic1['device'] = res[0]["name"]
            # lis2 = []
            # 查狱警组
            res2 = FlaskAPI.query_follow_group_workman(i['id'])
            lis3 = []

            for j in res2:
                # dic2 = {}

                # 查狱警name, chest_card_id
                res3 = FlaskAPI.query_workman_info(j['group_id'])
                print(333, res3)
                for z in res3:
                    dic3 = {}
                    # 查狱警设备device_id
                    res4 = FlaskAPI.query_workman_device_id(z['chest_card_id'])
                    print(222, res4)
                    dic3["name"] = z['name']
                    print(111, res4[0]['name'])
                    dic3['device'] = res4[0]['name']
                    # dic3[z['name']] = res4[0]['name']
                    lis3.append(dic3)
            dic1['workman'] = lis3
                # lis2.append(dic2)
            # 查犯人组
            res22 = FlaskAPI.query_follow_group_prison(i['id'])
            lis33 = []

            for j in res22:
                # dic22 = {}

                # 查狱警name, chest_card_id
                res33 = FlaskAPI.query_prison_info((j['group_id']))

                for z in res33:
                    dic33 = {}
                    # 查狱警设备device_id
                    res44 = FlaskAPI.query_prison_device_id(z['bracelet_id'])

                    dic33["name"] = z['name']
                    dic33["device"] = res44[0]['name']
                    lis33.append(dic33)
            dic1['prison'] = lis33
                # lis2.append(dic22)
            lis1.append(dic1)
        num = FlaskAPI.page_group_counts()
        if len(lis1) != 0:
            lis1[0]['number'] = num[0]['count']
        return lis1




def print_ctl(sign):
    print('数据清洗开始执行!')
    now_time = datetime.datetime.now()  # 获取当前时间
    print(now_time)
    # next_time = now_time + datetime.timedelta(minutes=5)
    # print("=====", next_time)
    next_time = now_time + datetime.timedelta(hours=1)
    # next_time = now_time + datetime.timedelta(hours=+0.01)
    x = datetime.datetime(next_time.year, next_time.month, next_time.day, next_time.hour, 0, 0)
    # x = datetime.datetime(next_time.year, next_time.month, next_time.day, next_time.hour, next_time.minute, 0)
    print("xx", x)
    y = datetime.datetime(now_time.year, now_time.month, now_time.day, now_time.hour, now_time.minute, now_time.second)
    print("yy", y)
    time_last = (x-y).total_seconds()
    print("-----", time_last)
    FlaskAPI.clear_sql('device_data', sign)
    timer1 = threading.Timer(time_last, print_ctl, args=(2,))
    print('数据清洗执行结束!')
    timer1.start()


def echart_ctl():
    now_time = datetime.datetime.now()  # 获取当前时间
    next_time = now_time + datetime.timedelta(hours=+1)
    x = datetime.datetime(next_time.year, next_time.month, next_time.day, next_time.hour, 0, 0)
    print(x)
    y = datetime.datetime(now_time.year, now_time.month, now_time.day, now_time.hour, now_time.minute, now_time.second)
    time_last = (x - y).total_seconds()
    z = datetime.datetime(now_time.year, now_time.month, now_time.day, now_time.hour, 59, 59)
    timeArray = time.strptime(z, "%Y-%m-%d %H:%M:%S")
    a_time = time.mktime(timeArray)
    FlaskAPI.query_number_person(a_time)
    # test1 = '2019-3-25 16:40:00'
    # timeArray = time.strptime(test1, "%Y-%m-%d %H:%M:%S")
    # aa = time.mktime(timeArray)
    print("aa", aa)
    timer1 = threading.Timer(time_last-1, echart_ctl, args=(2,))


def test1_ctl(sign):
    print('测试用例开始执行!')
    now_time = datetime.datetime.now()  # 获取当前时间
    # next_time = now_time + datetime.timedelta(hours=+1)
    next_time = now_time + datetime.timedelta(seconds=+1)
    # x = datetime.datetime(next_time.year, next_time.month, next_time.day, next_time.hour, 0, 0)
    x = datetime.datetime(next_time.year, next_time.month, next_time.day, next_time.hour, now_time.minute, now_time.second)
    y = datetime.datetime(now_time.year, now_time.month, now_time.day, now_time.hour, now_time.minute, now_time.second)
    time_last = (x-y).total_seconds()

    print('测试用例执行结束!')
    timer1 = threading.Timer(time_last, test1_ctl, args=(2,))
    print("ok")
    timer1.start()



# TODO 图表所需接口 By Wang

@app.route('/charlists')
def charlists():
    return render_template('charlists.html')

# TODO 查询警告信息表 By Wang
@app.route('/dataforcb_1', methods=['POST'])
def DashboardDataForCB_1():
    res = FlaskAPI.search_alarm_rule_for_cb()
    print(11111, res)
    a = {}
    b = []
    c = []
    for i in res:
        b.append(i["name"])
        c.append(i['id'])
    a['name'] = b
    a['告警程度'] = c
    return jsonify(a)


# TODO 查询各项告警信息接口
@app.route('/dataforcb_2', methods=['POST'])
def DashboardDataForCB_2():
    res = FlaskAPI.search_warn_for_cb()
    print(1111,res)
    return jsonify(res)


# TODO 查询设备数量接口
@app.route('/dataforcb_3', methods=['POST'])
def DashboardDataForCB_3():
    res = FlaskAPI.search_equipments_num_for_cb()
    print(1111, res)
    return jsonify(res)

# TODO 查询某一建筑内设备数量接口
@app.route('/counts_of_somebuilding', methods=['POST'])
def count_of_somebuilding():
    building_id = request.args.get('building_id')
    res = FlaskAPI.counts_of_some_building(building_id)
    return jsonify(res)

# # TODO: 查询建筑人员数量API
# class Chartperson(Resource):
#     def post(self):
#         # 查询实时数据中在建筑人员
#         pass

# TODO:设备分类数据展示
class DeviceDataShow(Resource):
    def post(self):
        data = request.json
        if data[0]["type"] == "1": # 基站
            res = FlaskAPI.device_data_show("equipment_base_station")
        elif data[0]["type"] == '2': # 门禁
            res = FlaskAPI.device_data_show("equipment_access_control")
        elif data[0]["type"] == '3': # 车禁
            res = FlaskAPI.device_data_show("equipment_vehicle_ban")
        elif data[0]["type"] == '4': # 周界
            res = FlaskAPI.device_data_show("equipment_perimeter")
        elif data[0]["type"] == '5': # 摄像头
            res = FlaskAPI.device_data_show("equipment_camera")
        elif data[0]["type"] == '6': # 一键报警
            res = FlaskAPI.device_data_show("equipment_call_police")
        elif data[0]["type"] == '7': # 车载摄像头
            res = FlaskAPI.device_data_show("equipment_car_camera")
        elif data[0]["type"] == '8': # 胸牌
            res = FlaskAPI.device_data_show("equipment_chest_card")
        elif data[0]["type"] == '9': # 手环
            res = FlaskAPI.device_data_show("equipment_bracelet")
        elif data[0]["type"] == '10': # 车辆
            res = FlaskAPI.device_data_show("equipment_car")
        else:
            return "数据类型错误"
        return res


# TODO: ERP设备信息同步3D接口
class DeviceTo3D(Resource):
    def get(self):
        data1 = FlaskAPI.read('equipment_base_station')
        data2 = FlaskAPI.read('equipment_access_control')
        data3 = FlaskAPI.read('equipment_vehicle_ban')
        data4 = FlaskAPI.read('equipment_perimeter')
        data5 = FlaskAPI.read('equipment_camera')
        data6 = FlaskAPI.read('equipment_call_police')
        # data7 = FlaskAPI.read('equipment_car_camera')
        data = data1 + data2 + data3 + data4 + data5 + data6
        return data

def flask_run():
    app.run(host='0.0.0.0', port=8080)


api.add_resource(Fun1, '/write_data/<table>', endpoint="aaa")
api.add_resource(Fun2, '/search_data/<table>', endpoint="bbb")
api.add_resource(Fun4, '/things/api', endpoint="ddd")
api.add_resource(Fun5, '/get/device_data', endpoint="eee")
api.add_resource(Fun6, '/fence_data/list', endpoint="fff")
api.add_resource(Fun7, '/insert/fence', endpoint="ggg")
api.add_resource(Fun8, '/things/info', endpoint="hhh")
api.add_resource(Fun9, '/ref/info', endpoint="iii")
api.add_resource(Test1, '/test/test1', endpoint='jjj')
api.add_resource(Alarm_border, '/alarm/border', endpoint='kkk')
api.add_resource(Drag, '/drag', endpoint='lll')
api.add_resource(Query_build, '/search_data/prison_building', endpoint='mmm')
api.add_resource(Query_room, '/search_data/prison_room', endpoint='nnn')
api.add_resource(Query_boundary, '/search_data/prison_boundary', endpoint='aa')
api.add_resource(Insert_visual_angle, '/insert/visual_angle', endpoint='bb')
api.add_resource(Query_visual_angle, '/query/visual_angle', endpoint='cc')
api.add_resource(InsertRoomInfo, '/insert/roomInfo', endpoint='dd')
api.add_resource(InsertBuildingInfo, '/insert/buildingInfo', endpoint='ee')
api.add_resource(InsertCorridorInfo, '/insert/corridorInfo', endpoint='de')
api.add_resource(QueryDevice, '/query/deviceInfo', endpoint='ff')
api.add_resource(QueryGroup, '/query/groupInfo', endpoint='gg')
api.add_resource(QueryPerson, '/query/personInfo', endpoint='hh')
api.add_resource(QueryFence, '/query/fenceInfo', endpoint='ii')
api.add_resource(QueryDeviceData, '/query/deviceData', endpoint='jj')
api.add_resource(QueryPrisonRoom, '/prison_room', endpoint='kk')
api.add_resource(StaticData, '/staticdata', endpoint='ll')
api.add_resource(BData, '/bdata', endpoint='mm')
api.add_resource(CarData, '/cccdata', endpoint='nn')
api.add_resource(MData, '/mdata', endpoint='a')
api.add_resource(Dupdate, '/dupdate', endpoint='b')
api.add_resource(Func1, '/getroomcorridor', endpoint='c')
# api.add_resource(Chartperson, '/api/chartperson', endpoint='apia')
api.add_resource(Imginfo, '/api/getImginfo', endpoint='apib')
api.add_resource(Guiji, '/api/guiji', endpoint='apic')
api.add_resource(BuildingNumber1, '/query/buildingnumber', endpoint='apid')
api.add_resource(PersonNumQuery, '/personnumquery', endpoint='apie')
api.add_resource(PersonListQuery, '/personlisquery', endpoint='apif')
api.add_resource(PersonInfoQuery_3D, '/personinfoquery3D', endpoint='apig')
api.add_resource(RealtimeInfoQuery, '/realtimeinfoquery', endpoint='apih')
api.add_resource(RealtimeAllInfo, '/realtimeallinfo', endpoint='apim')
api.add_resource(RealtimeDeviceNum, '/realtimedevicenum', endpoint='apin')
api.add_resource(RealtimePerson, '/realtimeperson', endpoint='apiqq')
api.add_resource(RealtimeDeviceQuery, '/realtimedevicequery', endpoint='apiww')
api.add_resource(DeviceNumQuery, '/devicenumquery', endpoint='apirr')
api.add_resource(DeviceAlarmQuery, '/devicealarmquery', endpoint='apitt')
api.add_resource(RealtimeDeviceinfoQuery, '/realtimedeviceinfoquery', endpoint='apiyy')
api.add_resource(DeviceDataShow, '/devicedatashow', endpoint='apiuu')
api.add_resource(Fence_init, '/fenceinit', endpoint='apiii')
api.add_resource(HeatingPower, '/heatingpower', endpoint='apioo')
api.add_resource(Followgroup, '/followgroup', endpoint='apipp')
api.add_resource(DeviceTo3D, '/deviceto3d', endpoint='apiaa')
api.add_resource(FenceAlarm, '/fencealarm', endpoint='apiss')
api.add_resource(PageFenceAlarm, '/pagefencealarm', endpoint='apidd')
api.add_resource(AllAlarm, '/allalarm', endpoint='apiff')
api.add_resource(PageAllAlarm, '/pageallalarm', endpoint='apigg')
api.add_resource(DelHisAlarm, '/delhisalarm', endpoint='apihh')
api.add_resource(MarkInsert, '/markinsert', endpoint='apijj')
api.add_resource(MarkQuery, '/markquery', endpoint='apikk')
api.add_resource(MarkDel, '/markdel', endpoint='apill')
api.add_resource(GetFollowGroup, '/getfollowgroup', endpoint='apizz')
api.add_resource(ERPDeviceNumQuery, '/erpdevicenum', endpoint='apixx')
api.add_resource(FenceDel, '/fencedel', endpoint='apicc')
api.add_resource(FollowAlarmToday, '/followalarmtoday', endpoint='apivv')
api.add_resource(FollowAlarmHistory, '/followalarmhistory', endpoint='apibb')
api.add_resource(BoundAlarmToday, '/boundalarmtoday', endpoint='apinn')
api.add_resource(AbnormalAlarmToday, '/abnormalalarmtoday', endpoint='apimm')
api.add_resource(PersonAlarmToday, '/personalarmtoday', endpoint='apiqa')
api.add_resource(FollowgroupAll, '/followgroupall', endpoint='apiws')
api.add_resource(HistoryAlarmToday, '/historytoday', endpoint='apied')
api.add_resource(CircumDevice, '/circumdevice', endpoint='apirf')
api.add_resource(TodayAlarm, '/todayalarm', endpoint='apitg')
api.add_resource(DeviceNumber1, '/devicenumber1', endpoint='apiyh')
api.add_resource(ConditionAlarmFind, '/conditionfind', endpoint='apiuj')
api.add_resource(ConditionFollowFind, '/conditionfindfollow', endpoint='apiik')
if __name__ == '__main__':
    # sys.setrecursionlimit(10000000)
    # master = sentinel.master_for('mymaster', socket_timeout=0.5, password='redis_auth_pass', db=15)
    # w_ret = master.set('foo', 'bar')
    # print(w_ret)
    # # 获取从服务器进行读取
    # # slave = sentinel.slave_for('mymaster', socket_timeout=0.5, password='redis_auth_pass', db=15)
    # r_ret = slave.get('foo')
    # print(r_ret)
    # t1 = time.time()
    # print(int(t1))
    # t2 = 'Fence' + str(int(t1))
    # print(t2)
    # print('t1', t1)
    # test1 = '2019-3-25 16:40:00'
    # timeArray = time.strptime(test1, "%Y-%m-%d %H:%M:%S")
    # aa = time.mktime(timeArray)
    # print("aa", aa)
    # test1 = '2019-3-25 16:40:01'
    # timeArray = time.strptime(test1, "%Y-%m-%d %H:%M:%S")
    # bb = time.mktime(timeArray)
    # print("bb", bb)
    # timer1 = threading.Timer(1, print_ctl, args=(1,))
    timer2 = threading.Timer(1, flask_run)
    # timer1.start()
    timer2.start()
    print("finishing-------------------------------------------")
