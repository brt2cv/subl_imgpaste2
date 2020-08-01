ImgPaste2
==========
Forked from https://github.com/robinchenyu/imagepaste

## 功能

+ [x] Windows下，仍使用PIL进行图像的粘贴；
+ [x] 支持Linux系统下，实现对剪切板图像的处理调用（Ctrl+V)；
+ [x] 默认使用JPG的方式保存，可以显著减小图片的存储体积；
+ [x] 删除原版程序中 `图片预览` & `截屏工具` 的功能，只保留核心项：粘贴；

## 安装

```sh
cd ~/.config/sublime-text-3/Packages
git clone https://gitee.com/brt2/subl_imgpaste2.git
```

## 依赖

Linux

* Pillow
* PyQt5

Windows

* Pillow

当然，你如果不想污染你的python系统环境，可以将下载的依赖包直接剪切到 `subl_imgpaste2/lib` 目录下。`imagepaste` 项目就是这样集成PIL的。
