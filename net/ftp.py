# Copyright (C) 2013, Tim Beatty
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from ftplib import FTP
import logging
from StringIO import StringIO


class FtpClient():
  def __init__(self, host='', user='', passwd=''):
    self.logger = logging.getLogger('FtpClient')
    self.host = host
    self.user = user
    self.passwd = passwd
  
  def connect(self):
    self.logger.info('Connecting to %s' % self.host)
    self.ftp = FTP(self.host, self.user, self.passwd)
    self.logger.debug(self.ftp.getwelcome())

  def write_file(self, filename, fp):
    return self.ftp.storbinary('STOR %s' % filename, StringIO(fp.read()))
    
  def disconnect(self):
    self.logger.info('Disconnecting from %s' % self.ftp.host)
    self.ftp.close()
