#!/usr/bin/env python3
# @Date    : 2020-07-02 14:53:29
# @Author  : brt2 (brt2@qq.com)
# @Version : 0.1.1

def save_clipboard_image(path, img, type_="JPEG"):
    if type_ == "JPEG" and img.mode != "RGB":
        img = img.convert("RGB")
    img.save(path, type_)
