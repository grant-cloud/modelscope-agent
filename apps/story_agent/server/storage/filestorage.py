import oss2
import os
from conf.config import OSS_API_KEY, OSS_API_SECRET, BUCKET_NAME, ENDPOINT, PREFIX


class FileStorage:
    def __init__(self):
        self.access_key_id = OSS_API_KEY
        self.access_key_secret = OSS_API_SECRET
        self.bucket_name = BUCKET_NAME
        self.endpoint = ENDPOINT
        self.auth = oss2.Auth(self.access_key_id, self.access_key_secret)
        self.bucket = oss2.Bucket(self.auth, self.endpoint, self.bucket_name)
        self.prefix = PREFIX

    def upload_file(self, oss_file_path, file_local_path):
        """
        :param oss_file_path: abc/efg/123.jpg
        :param file_local_path: /users/local/myfile.txt
        :return:
        """
        oss_path = os.path.join(self.prefix, oss_file_path)
        self.bucket.put_object_from_file(str(oss_path), file_local_path)

    def cover_to_url(self, oss_file_path, small_image=False):
        """
        :param oss_file_path:  abc/efg/123.jpg
        :param small_image: Whether to generate thumbnails.
        """
        oss_path = os.path.join(self.prefix, oss_file_path)
        if small_image:
            url = ('https://' + 'resouces.modelscope.cn/' +
                   str(oss_path) + '?x-oss-process=image/resize,w_210,h_280')
        else:
            url = 'https://' + 'resouces.modelscope.cn/' + str(oss_path)
        return url
