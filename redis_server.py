# coding:utf-8
from flask import Flask, jsonify, Response, render_template, make_response,session,request as req
from flask_restful import reqparse, abort, Api, Resource, request
from flask_cors import *
from flask_session import Session
import redis
app = Flask(__name__)
app.config.update(RESTFUL_JSON=dict(ensure_ascii=False))
CORS(app)
app.secret_key = 'aaaaaaaaaa'
app.debug = False
app.config['SESSION_TYPE'] = 'redis'  # session类型为redis
app.config['SESSION_PERMANENT'] = False # 如果设置为True，则关闭浏览器session就失效。
app.config['SESSION_USE_SIGNER'] = True  # 是否对发送到浏览器上session的cookie值进行加密
app.config['SESSION_KEY_PREFIX'] = 'session:'  # 保存到session中的值的前缀
app.config['SESSION_REDIS'] = redis.Redis(host='127.0.0.1', port='6379', decode_responses=False)  # 用于连接redis的配置
Session(app)
api = Api(app)

