import logging
import os
import sys
import atexit

logger = logging.getLogger(__name__)


def _create_pidfile(pid_file):
    pid = str(os.getpid())
    if os.path.isfile(pid_file):
        return False
    else:
        open(pid_file, 'w').write(pid)
    return True


def handle_pidfile(pid_file):
    logger.info('creating pidfile')
    if not _create_pidfile(pid_file):
        logger.error('pidfile exists: exiting')
        sys.exit(1)
    atexit.register(_remove_pid_file, pid_file)


def _remove_pid_file(pid_file):
    logger.info('removing pidfile')
    os.unlink(pid_file)