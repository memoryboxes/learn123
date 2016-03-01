import sys

from settings import BPC_PATH, NPMDATA_PATH, NPMWEB_PATH, SMARTPROBE_PATH

try:
    sys.path.append(NPMDATA_PATH)
    sys.modules['mycroft.npm'] = __import__('npm')
    import npm
except ImportError:
    pass

try:
    sys.path.append(NPMWEB_PATH)
    sys.modules['mycroft.npmweb'] = __import__('npmweb')
    import npm
except ImportError:
    pass

try:
    sys.path.append(BPC_PATH)
    sys.modules['mycroft.bpc'] = __import__('bpc')
    import bpc
except ImportError:
    pass

try:
    sys.path.append(SMARTPROBE_PATH)
    sys.modules['mycroft.smartprobe'] = __import__('portal')
    import smartprobe
except ImportError:
    pass

