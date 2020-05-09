#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 使い方
# $ ./tcpserver.py

import socket
import threading
import codecs
import os
import csv
import re

# 
# 設定（変更必須）
# 
bind_port = 34567

# 
# 設定（変更任意）
# 

# 受信データに対する送信データの対応表
recv_send_tbl = {
    '41':'414243', 
    '5a':'5a5a5a', 
}

# 以下は別ファイルにCSVでkey, value（受信データ, 送信データ）を指定する場合のファイル名
RECV_SEND_TBL_FILEPATH = './recv_send_tbl.csv'

bind_ip = "0.0.0.0" # ANY扱い = すべてのIPアドレスでlisten
SERVER_CONNECTION_NUM = 3 # 同時接続可能数

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((bind_ip, bind_port))

server.listen(SERVER_CONNECTION_NUM)  ### server while loop
print "Listening on %s: %d" % (bind_ip, bind_port)


def handle_client(client_socket, addr):
    while True:
        request = client_socket.recv(1024)
        if not request:
            # 切断時処理
            # TCP1接続が切れた状態で、client_socket.recvが実行されると
            # 空データが格納される。その場合はループを抜けてclose()させる
            print "Disconnected from: %s: %d" % (addr[0], addr[1])
            break
        else:
            recv_hexstr = codecs.encode(request, 'hex_codec') # 16進数文字列に変換
            send_hexstr = '73616d706c65' # "sample"
            print "Received: %s" % recv_hexstr
            
            # 以下は別ファイルにCSVでkey, value（受信データ, 送信データ）を指定する例
            if os.path.isfile(RECV_SEND_TBL_FILEPATH): 
                with open(RECV_SEND_TBL_FILEPATH, 'r') as f:
                    reader = csv.DictReader(f, fieldnames=['rcv', 'snd'], )
                    for row in reader:
                        # print(row)
                        # 変換表へ追加（同一のものが手動で登録されていた場合、上書き）
                        recv_send_tbl[ row['rcv'] ] = row['snd']
                        
            
            # 受信データと送信データの変換
            # 完全一致を優先、その後、正規表現による置換を試す（正規表現内は順不同）
            if recv_hexstr in recv_send_tbl: 
                # 完全一致
                send_hexstr = recv_send_tbl[recv_hexstr]
                print "Hit table: %s -> %s" % (recv_hexstr, send_hexstr)
            else: 
                # 正規表現も許容
                for key, value in recv_send_tbl.items():
                    if re.match(r"%s" % key, recv_hexstr):  # rでraw文字列指定しているので、バックスラッシュ等も指定可能
                        match = re.search(r"%s" % key, recv_hexstr)
                        send_hexstr = match.expand(r"%s" % value)
                        print "Match table: %s (pattern %s) -> %s" % (recv_hexstr, key, send_hexstr)
            
            client_socket.send( codecs.decode(send_hexstr, 'hex_codec') ) # 16進数文字列をバイナリに変換して送信
        
    client_socket.close()


while True:
    client, addr = server.accept()
    print "Accepted connection from %s: %d" % (addr[0], addr[1])
    client_handler = threading.Thread(target=handle_client, args=(client, addr))
    client_handler.start()
