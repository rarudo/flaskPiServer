# -*- coding: utf-8 -*-
from datetime import timedelta
from flask import Flask, request, make_response, session
import json
from statusManager import rpiStatus

app = Flask(__name__)

# 地図用アプリケーションのためのjson buffer
jsonBufferForMap = []
# 通信があったIPを格納しておく
aliveIpList = []
rpiStatus = rpiStatus()


@app.route('/', methods=['POST'])
def postJson():
    receiveStr = request.data.decode()
    print(receiveStr)
    # jsonをDictにして読み込み
    jsonDict = json.loads(receiveStr)
    # bufferに追加
    jsonBufferForMap.append(jsonDict)
    aliveIpList.append(jsonDict["ip"])
    # ラズパイとdockerのステータスを更新
    rpiStatus.refleshStatus(jsonDict["ip"])
    return "HelloFromServer\n"


@app.route('/getTask', methods=['GET'])
def getTask():
    global jsonBufferForMap
    count = len(jsonBufferForMap)
    if count > 400:
        count = 400
    responceJson = json.dumps(jsonBufferForMap[-count:])
    del jsonBufferForMap[-count:]
    return make_response(responceJson)


@app.route('/getAliveDockerIp', methods=['GET'])
def getAliveDockerIp():
    global aliveIpList
    aliveIpList = list(set(aliveIpList))
    responceJson = json.dumps(aliveIpList)
    del aliveIpList[:]
    return make_response(responceJson)


# dockerとラズパイの状態が保存られた配列をjsonにして返す
@app.route('/getDockerStatus', methods=['GET'])
def getDockerStatus():
    dict = {}
    # numpyをdictに直して、jsonにする
    for i, dockerstatus in enumerate(rpiStatus.getDockerStatuses().tolist()):
        name = "rpi" + str(i)
        dict.update({name: dockerstatus})
    return json.dumps(dict)


if __name__ == '__main__':
    app.debug = False
    app.run(host="192.168.98.28")
