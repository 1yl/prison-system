import redis
from redis.sentinel import Sentinel

# 连接哨兵服务器
sentinel = Sentinel([
    ('127.0.0.1', 26379),
    # ('127.0.0.1', 6381),
    # ('127.0.0.1', 6382)
], socket_timeout=0.5)

# # 获取主服务器地址
# master = sentinel.discover_master('host6380')
# # print(master)
# # 获取从服务器地址
# slave = sentinel.discover_slaves('host6380')
# print(slave)
# 获取主服务器进行写入
master = sentinel.master_for('host6380', socket_timeout=0.5, db=15)
# w_ret = master.set('foo', 'bar')
# print(w_ret)
# 获取从服务器进行读取
slave = sentinel.slave_for('host6380', socket_timeout=0.5, db=15)
# r_ret = slave.get('foo')
# print(r_ret)