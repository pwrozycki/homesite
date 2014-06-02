import os


def create_pidfile(location):
    pid = str(os.getpid())
    if os.path.isfile(location):
        return False
    else:
        open(location, 'w').write(pid)
    return True