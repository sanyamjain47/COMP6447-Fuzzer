from threading import Thread
import sys

class ThreadOutput(Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.output = None

    def run(self):
        if self._target is None:
            return  # could alternatively raise an exception, depends on the use case
        try:
            self.output = self._target(*self._args, **self._kwargs)
        except Exception as exc:
            print(f'{type(exc).__name__}: {exc}', file=sys.stderr)  # properly handle the exception

    def join(self, *args, **kwargs):
        super().join(*args, **kwargs)
        return self.output
