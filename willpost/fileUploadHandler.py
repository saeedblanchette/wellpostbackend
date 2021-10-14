from django.core.files.uploadhandler import MemoryFileUploadHandler, SkipFile, StopUpload
from rest_framework.exceptions import UnsupportedMediaType


class MyFileUploadHandler(MemoryFileUploadHandler):
    def receive_data_chunk(self, raw_data, start):
        try:
            super().receive_data_chunk(raw_data, start)
        except (SkipFile, StopUpload):
            print(' Stop Uploading  1')

    def upload_interrupted(self):
        print(' Stop Uploading  2')
        super().upload_interrupted()
        raise UnsupportedMediaType
