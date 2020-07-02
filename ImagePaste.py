import sublime
import sublime_plugin

import os
import sys
import subprocess


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

if path_bin not in sys.path:
    sys.path.append(path_bin)
from util import save_clipboard_image  # 调用本地模块

if sys.platform == 'win32':
    # 从集成的PIL中导入
    if path_lib not in sys.path:
        sys.path.append(path_lib)
    from PIL import ImageGrab, ImageFile
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
        print("[debug] subprocess.PIPE.stdin: {}".format(str_path.encode()))
        PROC.stdin.write(str_path.encode())  # need bytes
        PROC.stdin.flush()

        bytes_state = PROC.stdout.readline()  # bytes
        print("[debug] subprocess.PIPE.stdout:", str(bytes_state))
        return bytes_state == b"ok\n"

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
        print("Init ImageCommand -> image_dir=%r" % self.image_dir_name)

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
            rel_filename = os.path.join("%s/%s%d.jpg" % (self.image_dir_name if self.image_dir_name else fn_without_ext, fn_without_ext, i))
            # absolute file path
            path_abs = os.path.join(subdir_name, "%s%d.jpg" % (fn_without_ext, i))
            if not os.path.exists(path_abs):
                break
            i += 1

        print("[debug] Try to save file: " + path_abs)
        return path_abs, rel_filename


class ImagePasteCommand(ImageCmdInterface, sublime_plugin.TextCommand):
    def run(self, edit):
        rel_fn = self.paste()

        if not rel_fn:
            self.view.run_command("paste")
            return

        for pos in self.view.sel():
            print("scope name: %r" % (self.view.scope_name(pos.begin())))
            if 'text.html.markdown' in self.view.scope_name(pos.begin()):
                self.view.insert(edit, pos.begin(), "![](%s)" % rel_fn)
            else:
                self.view.insert(edit, pos.begin(), "%s" % rel_fn)
            # only the first cursor add the path
            break

    def paste(self):
        path_save, rel_fn = self.get_filename()
        if sys.platform == 'win32':
            img = ImageGrab.grabclipboard()
            if img:
                path_save = sys.argv[1] if sys.argv[1] else "save.jpg"
                save_clipboard_image(path_save, img)
                print("[+] Save Image to 【{}】." % path_save)
                return rel_fn
        else:
            # img = grabclipboard_byQt(cb, "img")
            if call_subproc(path_save):
                return rel_fn

        print('[-] Clipboard buffer is not IMAGE!')
        return None
