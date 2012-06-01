from pdataparser import PDataParser
from config import *
from pytz import timezone
import datetime
import urllib
import pg
import signal
import sys
import socket
import base64
import atexit
import urllib
import math
import os

class PDataSpider:
    "PData Spider"
    
    def __init__(self):
        self.log_f = open(log_output_file, 'a')
        socket.setdefaulttimeout(20)
        signal.signal(signal.SIGINT, self.quit_signal_handler)
        atexit.register(self.__destructor__)
        
    def __destructor__(self):
        self.log_f.close()