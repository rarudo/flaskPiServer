import numpy as np
import ipaddress
from datetime import datetime


class rpiStatus:
    def __init__(self):
        # 想定ネットワーク
        self.networks = [
            ipaddress.ip_network("192.168.0.0/24"),
            ipaddress.ip_network("192.168.1.0/24"),
            ipaddress.ip_network("192.168.2.0/24"),
            ipaddress.ip_network("192.168.3.0/24"),
            ipaddress.ip_network("192.168.4.0/24"),
            ipaddress.ip_network("192.168.5.0/24"),
            ipaddress.ip_network("192.168.6.0/24"),
            ipaddress.ip_network("192.168.7.0/24"),
        ]

        # 想定するラズパイの数
        self.rpiMount = 8
        # 想定するdockerの数
        self.dockerMount = 20

        # タイムアウト（秒）
        self.timeout = 4

        # 全てのDockerのステータス、8x21の行列初期値は全てFalse
        self.dockerAccesses = np.zeros((self.rpiMount, self.dockerMount), dtype=bool)
        # 全てのラズパイのステータス、1x8の行列初期値は全てFalse
        self.rpiStatuses = np.zeros((self.rpiMount), dtype=bool)
        # アクセスのあった時間を格納する
        # self.accesTimes = np.array((self.rpiMount, self.dockerMount), dtype='datetime64')
        # self.accesTimes.fill(datetime.now())
        self.accessTimes = np.empty((self.rpiMount, self.dockerMount), dtype='datetime64[ms]')
        self.accessTimes.fill(np.datetime64(datetime.now()))

    # ipアドレスがnetworksの何番目に含まれているのかを返す
    # 含まれていない場合はNone
    def getNwIndex(self, ip):
        index = None
        for i, nw in enumerate(self.networks):
            if ip in nw:
                index = i
        return index

    def getDockerStatuses(self):
        nowTimes = np.empty((self.rpiMount, self.dockerMount), dtype='datetime64[ms]')
        nowTimes.fill(np.datetime64(datetime.now()))

        # 何秒前にアクセスされたかを計算
        diffTimes = (nowTimes - self.accessTimes)
        # timeout秒以内にアクセスされていればTrueいなければFalse
        diffBool = (diffTimes < np.datetime64(self.timeout, 's').astype("m8[s]"))
        # 論理和を返す
        # アクセスかつn秒以内にアクセスがあればTrue
        return np.logical_and(diffBool, self.dockerAccesses)

    def getRpiStatuses(self):
        dockersArray = self.getDockerStatuses()
        rowCont = dockersArray.shape[0]
        for i in range(rowCont):
            print("hoge")

        return ""

    # 引数に入れられたipからステータスを更新する
    # postされた時に呼ばれる
    def refleshStatus(self, ipStr):
        # 文字列で渡されたipをpythonのipadressに変換
        ip = ipaddress.ip_address(ipStr)

        # ipアドレスからどのネットワークかを判別
        # これでどのラズパイから送られたものかがわかる
        nwIndex = self.getNwIndex(ip)

        # 想定外のipだったら何もしない
        if nwIndex is None:
            print("ipが想定されているネットワークに含まれていない")
            return

        # どのdockerから送られているか判別用
        # ipアドレスの第四セグメントを取得する
        # ipを192.168.1.100, 192,168,1.101
        # と想定しているため、00 01を取得したい
        dockerId = ipStr.split(".")[-1]
        dockerId = int(dockerId[-2:])
        self.rpiStatuses[nwIndex] = True
        self.dockerAccesses[nwIndex][dockerId] = True
        # アクセスされた時間を格納
        self.accessTimes[nwIndex][dockerId] = np.datetime64(datetime.now())
