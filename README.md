ImgPaste2
==========
Forked from https://github.com/robinchenyu/imagepaste

## 功能

+ [x] 支持Windows/Linux系统下，实现对剪切板图像的处理调用（Ctrl+Shift+V）；
+ [x] 默认使用JPG的方式保存，可以显著减小图片的存储体积；
+ [x] 删除原版程序中 `图片预览` & `截屏工具` 的功能，只保留核心项：`图像粘贴` ；
    * 对剪切板图像保存到本地并在Markdown文本中插入链接地址
    * 对剪切板中的图像地址，直接插入到Markdown文本中

## 安装

```sh
cd ~/.config/sublime-text-3/Packages
git clone https://gitee.com/brt2/subl_imgpaste2.git
```

## 依赖

Linux

* Pillow（已集成）
* PyQt5 - 需要系统Python3环境中安装

Windows（均已集成）

* Pillow
* pyperclip
