from datetime import timedelta

from flask import Flask, request, make_response, session
import json
from statusManager import rpiStatus

app = Flask(__name__)

jsonBuffer = []
rpiStatus = rpiStatus()


@app.route('/', methods=['POST'])
def hello_world():
    global jsonBuffer

    receiveStr = request.data.decode()
    print(receiveStr)
    # jsonをDictにして読み込み
    jsonDict = json.loads(receiveStr)
    # bufferに追加
    jsonBuffer.append(jsonDict)
    # ラズパイとdockerのステータスを更新
    rpiStatus.refleshStatus(jsonDict["ip"])
    return "HelloFromServer\n"


@app.route('/getTask', methods=['GET'])
def getTask():
    global jsonBuffer
    count = len(jsonBuffer)
    if count > 200:
        count = 200
    responceJson = json.dumps(jsonBuffer[-count:])
    del jsonBuffer[-count:]
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
    app.run(host="192.168.98.28")
