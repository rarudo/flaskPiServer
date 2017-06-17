# -*- coding: utf-8 -*-
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
        #self.networks = [
        #    ipaddress.ip_network("5.150.156.0/24"), #America
        #    ipaddress.ip_network("27.133.174.0/24"),#Japan
        #    ipaddress.ip_network("1.10.11.0/24"), #China
        #    ipaddress.ip_network("31.210.136.0/24"), #Russia
        #    ipaddress.ip_network("45.220.49.0/24"), #Africa
        #    ipaddress.ip_network("36.37.38.0/24"), #Australia
        #    ipaddress.ip_network("170.80.5.0//24"), #Brazil
        #    ipaddress.ip_network("86.105.227.0/24"), #Europe
        #]

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
