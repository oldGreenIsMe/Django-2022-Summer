# -*- coding: UTF-8 -*-
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse


class ImageStorage(FileSystemStorage):
    from django.conf import settings

    def __init__(self, location=settings.MEDIA_ROOT, base_url=settings.MEDIA_URL):
        # 初始化
        super(ImageStorage, self).__init__(location, base_url)

    # 重写 _save方法
    def _save(self, name, content):  # name为上传文件名称
        import os
        import time
        import random
        # 文件扩展名
        ext = os.path.splitext(name)[1]
        # 文件目录
        d = os.path.dirname(name)
        # 定义文件名
        fn = time.strftime('%Y_%m_%d_%H_%M_%S')
        # 重写合成文件名
        name = os.path.join(d, fn + ext)
        # 调用父类方法
        return super(ImageStorage, self)._save(name, content)


class ProtoStorage(FileSystemStorage):
    from django.conf import settings

    def __init__(self, location=settings.MEDIA_ROOT, base_url=settings.MEDIA_URL):
        super(ProtoStorage, self).__init__(location, base_url)

    def _save(self, name, content):
        import os
        import time
        ext = os.path.splitext(name)[1]
        d = os.path.dirname(name)
        fn = time.strftime('%Y_%m_%d_%H_%M_%S')
        name = os.path.join(d, fn + ext)
        return super(ProtoStorage, self)._save(name, content)
