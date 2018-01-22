#!/usr/bin/env python
# -*- coding:utf-8 -*-

from contextlib import closing
import cPickle
import cv2
import select
import socket
import sys
import urllib2

from mytoolbox import emphasize

# As a proxy

def wget_server(host='', port=55555, bufsize=1024**3, backlog=10):
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if host == '':
        cur_ip = socket.gethostbyname(host)
        emphasize('http://%s:%d' % (cur_ip, port))
    writefds = set()
    try:
        server_sock.bind((host, port))
        server_sock.listen(backlog)
        while True:
            if len(writefds) > 0:
                wready = select.select([], writefds, [])[1]
            else:
                wready = set()
            for sock in wready:
                url = cPickle.loads(sock.recv(bufsize))
                print 'Downloading %s...' % url,
                try:
                    data = urllib2.urlopen(url).read()
                    print 'Success.',
                except Exception as e:
                    # TODO
                    print 'Failure.'
                    print e
                    raise Exception()
                sock.send(data)
                print 'Data has been sent.'
                sock.close()
                writefds.remove(sock)
            conn, _ = server_sock.accept()
            writefds.add(conn)
    finally:
        for sock in writefds:
            sock.close()
        server_sock.close()

def ask_wget(url, host, port=55555, fname=None, bufsize=1024**3):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    with closing(sock):
        sock.connect((host, port))
        sock.send(cPickle.dumps(url))
        received = sock.recv(bufsize)
        if fname is None:
            fname = url.split('/')[-1]
        f = open(fname, 'wb')
        f.write(received)
        f.close()

if __name__ == '__main__':
    if len(sys.argv) == 1:
        wget_server(host='')
    else:
        test_url = sys.argv[1]
        ## or,
        # test_url = 'http://dlmarket-jp.s3.amazonaws.com/images/consignors/98/9871/test.jpg'
        # test_url = 'https://www.google.co.jp'
        ask_wget(test_url, host='')
