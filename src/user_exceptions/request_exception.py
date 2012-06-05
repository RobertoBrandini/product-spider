class RequestException(Exception):
    Name = "RequestException"
    def __init__(self, value, msg):
        self.value = value
        self.msg = msg
    def __str__(self):
        return repr(self.value) + "\n" + self.msg