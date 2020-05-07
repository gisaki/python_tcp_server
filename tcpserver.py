#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 使い方
# $ ./tcpserver.py

import socket
import threading
import codecs

bind_ip = "0.0.0.0" # ANY扱い = すべてのIPアドレスでlisten
bind_port = 34567

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((bind_ip, bind_port))

server.listen(3)  ### server while loop
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
            send_hexstr = '234567'
            print "Received: %s" % recv_hexstr
            
            # 以下は例
            if recv_hexstr == '3031':
                send_hexstr = '3030303031313131'
            elif recv_hexstr == '303132':
                send_hexstr = '303030303131313132323232'
            
            client_socket.send( codecs.decode(send_hexstr, 'hex_codec') ) # 16進数文字列をバイナリに変換して送信
        
    client_socket.close()


while True:
    client, addr = server.accept()
    print "Accepted connection from %s: %d" % (addr[0], addr[1])
    client_handler = threading.Thread(target=handle_client, args=(client, addr))
    client_handler.start()
