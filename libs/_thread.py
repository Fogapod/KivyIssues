import threading


def thread(func):
    def execute(*args, **kwargs):
        threading.Thread(target=func, args=args, kwargs=kwargs).start()

    return execute
