import os
from django.conf import settings
from configx.core.loader import XMLLoader
from configx.core.generic import ReadOnlyConfig, ReadWriteConfig

'''
local/default config
'''
class LocalDefaultMixin(object):

    base_path = os.path.join(settings.ETC_ROOT, "system")
    endpoint = None
    loader_class = XMLLoader

    @classmethod
    def get_file(cls, **kwargs):
        local_file = os.path.join(cls.base_path, "local", "%s.%s" %(cls.endpoint, cls.loader_class.suffix))
        if os.path.isfile(local_file):
            return local_file
        else:
            return os.path.join(cls.base_path, "default", "%s.%s" %(cls.endpoint, cls.loader_class.suffix))

    def get_loader_context(self):
        return {"root": self.endpoint, "file_path": self._file}


class LocalDefaultReadOnlyConfig(LocalDefaultMixin,
                                 ReadOnlyConfig):
    pass

class LocalDefaultReadWriteConfig(LocalDefaultMixin,
                                  ReadWriteConfig):
    pass
