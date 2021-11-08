#!/usr/bin/env python3
# @Date    : 2020-11-08
# @Author  : brt2 (brt2@qq.com)
# @Version : 0.1.2

DENSITY_LARGE_THRESHOLD = 0.15
SIZE_LARGE_THRESHOLD = (800, 800)


#####################################################################
# imgfmt@Version : 0.1.9
#####################################################################
from PIL import Image

def size_resolution(pil_img, thresh):
    """ thresh should be a tuple like (960, 480), and w >= h """
    w, h = pil_img.size
    if w < h:
        w, h = h, w
    return w <= thresh[0] and h <= thresh[1]

def resize(im, **kwargs):
    """
    kwargs:
        ratio: 缩放比例
        output_shape: list(w, h)
        min_size: 忽略存储空间小于此数值的小图片
        max_shape: 若为None，则正常缩放一次
                   否则递归压缩尺寸高于此数值的大图片, type: list(w, h)
        antialias: 开启抗锯齿（会增加图像的处理时长，默认开启）
        save_as_jpg: 强制将图像转换为jpg格式
    """
    default_kwargs = {
        "ratio": 0.5,
        "output_shape": None,
        # "min_size": 0,
        "max_shape": None,
        "antialias": True,
        "save_as_jpg": True
    }
    default_kwargs.update(kwargs)
    kwargs = default_kwargs

    # if os.path.getsize(path_src) < kwargs["min_size"]:
    #     return

    # 开启抗锯齿，耗时增加8倍左右
    resample = Image.ANTIALIAS if kwargs["antialias"] else Image.NEAREST

    # im = Image.open(path_src)
    if im.mode == "RGBA":  # and kwargs["save_as_jpg"]:
        im = im.convert("RGB")

    if kwargs["output_shape"]:
        w, h = kwargs["output_shape"]
        im_new = im.resize((w, h), resample)
    elif kwargs["max_shape"] is None:  # 执行一次缩放
        # 注意：pillow.size 与 ndarray.size 顺序不同
        list_ = [int(i*kwargs["ratio"]) for i in im.size]
        im_new = im.resize(list_, resample)
    else:  # 递归缩减
        while True:
            w, h = im.size
            if w <= kwargs["max_shape"][0] and h <= kwargs["max_shape"][1]:
                break
            w, h = [int(i*kwargs["ratio"]) for i in im.size]
            im = im.resize((w, h), resample)
        im_new = im

    # if kwargs["save_as_jpg"]:
    #     im_new.save(path_src, "JPEG", optimize=True, quality=85)
    # else:
    #     im_new.save(path_src, optimize=True)
    return im_new

#####################################################################
# end of imgfmt
#####################################################################

def save_clipboard_image(path, img, type_="JPEG"):
    if type_ == "JPEG" and img.mode != "RGB":
        img = img.convert("RGB")

    if not size_resolution(img, SIZE_LARGE_THRESHOLD):
        img = resize(img, ratio=0.8, max_shape=SIZE_LARGE_THRESHOLD)
        # print(f"已缩放【{path_img}】")

    img.save(path, type_)
