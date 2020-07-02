import sublime
import sublime_plugin

import os
import sys
import subprocess

# from bin.Clipboard import save_clipboard_image


if sys.platform == 'win32':
    # 从集成的PIL中导入
    package_file = os.path.normpath(os.path.abspath(__file__))
    package_path = os.path.dirname(package_file)
    lib_path =  os.path.join(package_path, "lib")
    if lib_path not in sys.path:
        sys.path.append(lib_path)
    from PIL import ImageGrab, ImageFile
    ImageFile.LOAD_TRUNCATED_IMAGES = True

else:
    # 通过PyQt5调用剪切板
    dirname = os.path.dirname(__file__)
    command =['python3', os.path.join(dirname, 'bin/clipboard.py')]
    str_cmd = " ".join(command)


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
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd, env=os.environ)

        try:
            outs, errs = proc.communicate(timeout=15)
        except Exception:
            proc.kill()
            outs, errs = proc.communicate()
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
        if not os.path.lexists(subdir_name):
            os.mkdir(subdir_name)

        i = 0
        while True:
            # relative file path
            rel_filename = os.path.join("%s/%s%d.png" % (self.image_dir_name if self.image_dir_name else fn_without_ext, fn_without_ext, i))
            # absolute file path
            path_abs = os.path.join(subdir_name, "%s%d.png" % (fn_without_ext, i))
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
        path_abs, rel_fn = self.get_filename()
        if sys.platform == 'win32':
            img = ImageGrab.grabclipboard()
            if im:
                im.save(path_abs, 'JPEG')
                return rel_fn
        else:
            str_cmd_curr = str_cmd + " " + path_abs
            out = self.run_command(str_cmd_curr)
            if out and out[:4] == "done":
                return rel_fn

        print('[-] Clipboard buffer is not IMAGE!')
        return None
