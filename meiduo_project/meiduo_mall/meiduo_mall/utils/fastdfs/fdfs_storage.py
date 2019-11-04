from django.core.files.storage import Storage
from django.conf import settings
from fdfs_client.client import Fdfs_client


class FastDFSStorage(Storage):
    """自定义文件存储系统，修改存储的方案"""
    def __init__(self, client_conf=None, fdfs_base_url=None):
        """
        构造方法，可以不带参数，也可以携带参数
        :param base_url: Storage的IP
        """
        """FDFS自定义文件存储类"""
        if client_conf is None:
            client_conf = settings.FASTDES_PATH

        self.client_conf = client_conf

        if fdfs_base_url is None:
            fdfs_base_url = settings.FDFS_BASE_URL

        self.fdfs_base_url = fdfs_base_url

    def _open(self, name, mode='rb'):
        """
        打开文件时会被调用，必须重写，文档说明
        :param name: 文件路径
        :param mode: 文件打开方式
        :return: None
        """
        # 因为当前不需要使用所以pass
        pass

    def _save(self, name, content):
        """
        保存文件会被调用，必须重写，文档说明
        :param name: 文件路径
        :param content: 文件二进制内容
        :return: None
        """
        client = Fdfs_client(self.client_conf)

        # 上传文件到FDFS系统
        res = client.upload_by_buffer(content.read())

        if res.get('Status') != 'Upload successed.':
            raise Exception('上传文件到FDFS系统失败')

        # 获取返回的文件id
        file_id = res.get('Remote file_id')

        return file_id


    def exists(self, name):
        """
        判断上传文件的名称和文件系统中原有的文件名是否冲突
        name: 上传文件的名称
        """
        return False


    def url(self, name):
        """
        返回name所指文件的绝对URL
        :param name: 要读取文件的引用:group1/M00/00/00/wKhnnlxw_gmAcoWmAAEXU5wmjPs35.jpeg
        :return:文件全路径 http://192.168.103.158:8888/group1/M00/00/00/wKhnnlxw_gmAcoWmAAEXU5wmjPs35.jpeg
        """
        # return 'http://192.168.152.10:8888/' + name
        # return 'http://image.meiduo.site:8888/' + name
        return self.fdfs_base_url + name