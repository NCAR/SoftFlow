
class openjson():
    MAX_RETRIES = 5
    def __init__(self, filepath, *args, **kwargs):
        self.filepath = filepath
        self.args = args
        self.kwargs = kwargs
        self.retries = 0
        self.fh = None
    def __enter__(self):
        try:
            self.fh = open(self.filepath, *self.args, **self.kwargs)
            return self.fh
        except Exception as e:
            print str(e)
            time.sleep(0.5)
            self.retries += 1
            if self.retries > self.MAX_RETRIES: return
    def __exit__(self, type, value, traceback):
        if self.fh is not None:
            self.fh.close()
            self.fh = None

