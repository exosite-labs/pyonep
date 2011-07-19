class OneException(Exception):
  pass

class OnePlatformException(OneException):
  def __init__(self, message):
    self.message = message

class JsonRPCRequestException(OneException):
  def __init__(self, message):
    self.message = message

class JsonRPCResponseException(OneException):
  def __init__(self, message):
    self.message = message

class JsonStringException(OneException):
  def __init__(self, message):
    self.message = message
