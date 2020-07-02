# @Date    : 2020-07-02
# @Author  : brt2 (brt2@qq.com)
# @Version : 0.1.2

from PIL import Image
from PyQt5.QtGui import QGuiApplication

def getclipboard(cb, type_=None):
    """ type_: text, img """
    ret = None
    if type_ == "text":
        if cb.mimeData().hasText():
            ret = cb.text()
    elif type_ == "img":
        if cb.mimeData().hasImage():
            qt_img = cb.image()
            ret = Image.fromqimage(qt_img)  # 转换为PIL图像
    else:
        raise Exception(f"未知的type_格式：「{type_}」")

    return ret

def save_clipboard_image(path, img, type_="JPEG"):
    if type_ == "JPEG" and img.mode != "RGB":
        img = img.convert("RGB")
    img.save(path, type_)


if __name__ == "__main__":
    import sys

    app = QGuiApplication([])
    cb = QGuiApplication.clipboard()
    # cb.dataChanged.connect()

    img = getclipboard(cb, "img")
    if img:
        path_save = sys.argv[1] if sys.argv[1] else "save.jpg"
        save_clipboard_image(path_save, img)
    #     print(f"Save Image to 【{path_save}】.")
    # else:
    #     print("Fail to catch a image from Clipboard.")
        print("done", end="")

    # app.exec()
    app.quit()
    sys.exit()
