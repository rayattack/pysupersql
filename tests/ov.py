

class Ov(object):

    def __init__(self, *args, **kwargs):
        self.a = 4

    def __eq__(self, b):
        return f"{self.a} = {b}"
