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

import logging

class FileWriter:
  def write(self, fp, metadata):
    pass

class FtpFileWriter(FileWriter):
  def __init__(self, ftp_client):
    self.logger = logging.getLogger('FtpFileWriter')
    self.ftp_client = ftp_client
  
  def write(self, fp, metadata):
    try:
      self.ftp_client.connect()
      filename = metadata['filename']
      self.logger.info('Writing file %s' % filename)
      self.ftp_client.write_file(filename, fp)
    finally:
      self.ftp_client.disconnect()
    
class S3FileWriter(FileWriter):
  def __init__(self, s3_client):
    self.logger = logging.getLogger('S3FileWriter')
    self.s3_client = s3_client
        
  def write(self, fp, metadata):
    try:
      self.s3_client.connect()
      bucket_name = metadata['bucket']
      self.logger.debug('Looking up bucket %s' % bucket_name)
      bucket = self.s3_client.lookup_bucket(bucket_name)
      if bucket is None:
        self.logger.debug('Creating bucket %s' % bucket_name)
        bucket = self.s3_client.create_bucket(bucket_name)
      key_name = metadata['key']
      self.logger.info('Writing key %s/%s' % (bucket_name, key_name))
      self.s3_client.write_key(bucket, key_name, fp, metadata)
    finally:
      self.s3_client.disconnect()
