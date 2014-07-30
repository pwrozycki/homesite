import sys
sys.path.append("/home/sandbox/pycharm-3.4.1/pycharm-debug-py3k.egg")

def settrace():
    import pydevd
    pydevd.settrace('localhost', port=6666, stdoutToServer=True, stderrToServer=True)