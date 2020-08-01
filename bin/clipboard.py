
# @Date    : 2020-07-02
# @Author  : brt2 (brt2@qq.com)
# @Version : 0.2.1

from PIL import Image
from PyQt5.QtGui import QGuiApplication

from util import save_clipboard_image

def grabclip_text(cb):
    if cb.mimeData().hasText():
        return cb.text()

def grabclip_img(cb):
    """ return a PIL_Image or None """
    if cb.mimeData().hasImage():
        # print("[+] Get image from the Clipboard.")
        qt_img = cb.image()
        return Image.fromqimage(qt_img)  # 转换为PIL图像
    # elif type_ == "text" and cb.mimeData().hasText():
    #     ret = cb.text()
    # else:
    #     raise Exception("未知的type_格式：「{}」" % type_)

grabclipboard_byQt = grabclip_img


if __name__ == "__main__":
    import sys

    app = QGuiApplication([])
    cb = QGuiApplication.clipboard()
    # cb.dataChanged.connect()

    # buff = ''
    # while True:
    #     x = sys.stdin.read(1)
    #     if not x:
    #         break
    #     buff += x
    #     if buff[-1] == "\n":
    #         path_save = buff[:-1]
    #         buff = ''
    #         # print(path_save, end="")

    for path_save in sys.stdin:
        # sys.stderr.write(path_save)
        # if path_save == "/home/brt/quit.jpg\n":
        #     break
        str_pip = "err"
        img = grabclipboard_byQt(cb)
        if img:
            save_clipboard_image(path_save.strip(), img)
            str_pipe = "img"
        else:
            text = grabclip_text(cb)
            # 验证是否为图像链接
            if text.startswith("http"):  # ?? 这里验证并不完整...
                str_pipe = text

        # sys.stdout.write(str_pipe + "\n")  # 必须添加换行符
        print(str_pipe)
        sys.stdout.flush()  # 及时清空缓存

    # app.exec()
    app.quit()
    sys.exit()
