import numpy as np
import ipaddress
from datetime import datetime

class rpiStatus:
    def __init__(self):
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

        # 全てのDockerのステータス、8x21の行列初期値は全てFalse
        self.dockerStatuses = np.zeros((self.rpiMount, self.dockerMount), dtype=bool)
        # 全てのラズパイのステータス、1x8の行列初期値は全てFalse
        self.rpiStatuses = np.zeros((self.rpiMount), dtype=bool)
        # アクセスのあった時間を格納する
        self.accesTimes = np.array((self.rpiMount, self.dockerMount))
        self.accesTimes.fill(datetime.now())


    # ipアドレスがnetworksの何番目に含まれているのかを返す
    # 含まれていない場合はNone
    def getNwIndex(self, ip):
        index = None
        for i, nw in enumerate(self.networks):
            if ip in nw:
                index = i
        return index

    # 引数に入れられたipからステータスを更新する
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

        # 結果を格納
        self.dockerStatuses[nwIndex][dockerId] = True
        self.rpiStatuses[nwIndex] = True
        # アクセスされた時間を格納
        self.accesTimes = datetime.now()
