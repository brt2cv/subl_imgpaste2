#!/usr/bin/env python3
# @Date    : 2020-07-02 17:40:52
# @Author  : brt2 (brt2@qq.com)
# @Version : 0.1.1

import os.path
import subprocess

dirname = os.path.dirname(__file__)
command =['python3', os.path.join(dirname, 'clipboard.py')]
# str_cmd = " ".join(command)
proc = subprocess.Popen(command,
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE)
                        # stderr=subprocess.STDOUT)

while proc.poll() is None:
    try:
        str_input = input("Please Input a path: ")
        if str_input == "quit":
            break

        bytes_path = f"/home/brt/{str_input}.jpg\n".encode()
        proc.stdin.write(bytes_path)
        proc.stdin.flush()

        bytes_state = proc.stdout.readline()  # bytes
        if bytes_state == b"ok\n":
            print("Well Done.")

    except subprocess.TimeoutExpired:
        print("子程序Timout未响应...")
        break

if proc.poll() is None:
    proc.kill()

