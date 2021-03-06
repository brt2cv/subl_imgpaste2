import sublime
import sublime_plugin

import os
import sys
import subprocess

from base64 import b64encode
from io import BytesIO
from hashlib import md5
from datetime import datetime

def subproc_init():
    # 通过PyQt5调用剪切板
    dirname = os.path.dirname(__file__)
    command =['python3', os.path.join(dirname, 'bin/clipboard.py')]
    # str_cmd = " ".join(command)
    return subprocess.Popen(command,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE)
                            # stderr=subprocess.STDOUT)

package_file = os.path.normpath(os.path.abspath(__file__))
package_path = os.path.dirname(package_file)
path_bin = os.path.join(package_path, "bin")
path_lib = os.path.join(package_path, "lib")

if path_lib not in sys.path:
    sys.path.append(path_lib)
if path_bin not in sys.path:
    sys.path.append(path_bin)
from util import format_clipboard_image  # 调用本地模块

if sys.platform == 'win32':
    # 从集成的PIL中导入
    from PIL import ImageGrab, ImageFile
    import pyperclip

    ImageFile.LOAD_TRUNCATED_IMAGES = True
else:
    PROC = subproc_init()

def subproc_stop():
    if PROC.poll() is None:
        PROC.kill()

def subproc_restart():
    global PROC

    print("[warning] 重启clipboard.py")
    subproc_stop()
    PROC = subproc_init()

def call_subproc(file_name):
    if PROC.poll() is not None:
        subproc_restart()

    try:
        str_path = file_name + "\n"
        print(">>> subprocess.PIPE.stdin:", str_path.encode())
        PROC.stdin.write(str_path.encode())  # need bytes
        PROC.stdin.flush()

        bytes_state = PROC.stdout.readline()  # bytes
        print(">>> subprocess.PIPE.stdout:", bytes_state.decode())
        return bytes_state  # == b"img\n"

    except subprocess.TimeoutExpired:
        print("子程序Timout未响应...")
        subproc_restart()


# def plugin_loaded():
#     """ 插件已载入 """
# def plugin_unloaded():
#     """ 卸载插件 """


class ImageCmdInterface:
    def __init__(self, *args, **kwgs):
        super().__init__(*args, **kwgs)
        self.settings = sublime.load_settings('imgpaste2.sublime-settings')

        # get the image save dirname
        self.image_dir_name = self.settings.get('image_dir_name', "")
        # print("Init ImageCommand -> image_dir=%r" % self.image_dir_name)

    def run_command(self, cmd):
        cwd = os.path.dirname(self.view.file_name())
        # print("[+] run cmd: %r" % cmd)
        PROC = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd, env=os.environ)

        try:
            outs, errs = PROC.communicate(timeout=15)
        except Exception:
            PROC.kill()
            outs, errs = PROC.communicate()
        print("[debug] outs %r, errs %r" % (b'\n'.join(outs.split(b'\r\n')), errs))
        # if errs is None or len(errs) == 0:
        return outs.decode()

    def get_filename(self):
        # create dir in current path with the name of current filename
        dirname, _ = os.path.splitext(self.view.file_name())

        # create new image file under currentdir/filename_without_ext/filename_without_ext%d.png
        fn_without_ext = os.path.basename(dirname)
        if self.image_dir_name:
            subdir_name = os.path.join(os.path.split(dirname)[0], self.image_dir_name)
        else:
            subdir_name = dirname
        if not os.path.exists(subdir_name):
            os.mkdir(subdir_name)

        i = 0
        while True:
            # relative file path
            dir_ = self.image_dir_name if self.image_dir_name else fn_without_ext + "/"
            file_name = "{}-{}.jpg".format(fn_without_ext, i)
            rel_filename = dir_ + file_name
            # absolute file path
            path_abs = os.path.join(subdir_name, file_name)
            if not os.path.exists(path_abs):
                break
            i += 1

        print("[debug] Try to save file: " + path_abs)
        return path_abs, rel_filename


class ImagePasteCommand(ImageCmdInterface, sublime_plugin.TextCommand):
    def run(self, edit):
        img_str = self.paste_image()

        if not img_str:
            self.view.run_command("paste")
            return

        for pos in self.view.sel():
            # print("scope name: %r" % (self.view.scope_name(pos.begin())))
            if 'text.html.markdown' in self.view.scope_name(pos.begin()):
                if isinstance(img_str, str):
                # if img_str.startswith("http"):
                    self.view.insert(edit, pos.begin(), "![](%s)" % img_str)
                else:
                    md5obj = md5(datetime.now())
                    md5obj.update(img_str)
                    tmp_label = md5obj.hexdigest()

                    self.view.insert(edit, pos.begin(), "![](%s)" % tmp_label)
                    self.view.insert(edit, pos.end(), "\n\n[%s](%s)" % (tmp_label, img_str.decode()))
            else:
                self.view.insert(edit, pos.begin(), "%s" % img_str)
            # only the first cursor add the path
            break

    def paste_image(self):
        # path_save, rel_fn = self.get_filename()
        if sys.platform == 'win32':
            img = ImageGrab.grabclipboard()
            if img:
                _resize = [0, 1]
                _resize.extend(img.size)
                img = format_clipboard_image(img.crop(_resize))  # 因黑边问题，裁剪掉首行像素
                # if save_clipboard_image:
                #     img.save(path, type_)
                # convert image to base64
                buff = BytesIO()
                img.save(buff, format='JPEG')
                img_base64 = b64encode(buff.getvalue())  # bytes
                return img_base64
            else:
                text = pyperclip.paste()
                if text.startswith("http"):
                    return text
        else:  # for Linux
            bytes_ret = call_subproc(path_save)
            if bytes_ret == b"img\n":
                return rel_fn
            elif bytes_ret != b"err\n":
                return bytes_ret.decode().strip()

        print('[-] Clipboard buffer is not IMAGE!')
        return
