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

import boto
from boto.s3.key import Key
from boto.s3.lifecycle import Lifecycle, Transition, Rule


def default_lifecycle():  # @NoSelf
  to_glacier = Transition(days=30, storage_class='GLACIER')
  rule = Rule('ruleid', 'logs/', 'Enabled', transition=to_glacier)
  lifecycle = Lifecycle()
  lifecycle.append(rule)
  return lifecycle

DEFAULT_LIFECYCLE = default_lifecycle()
  
class S3Client():
  def __init__(self, access_key_id=None, secret_access_key=None):
    self.logger = logging.getLogger('S3Client')
    self.access_key_id = access_key_id
    self.secret_access_key = secret_access_key
    
  def connect(self):
    self.conn = boto.connect_s3(self.access_key_id, self.secret_access_key)
    self.logger.info('Connected to %s' % self.conn.host)

  def create_bucket(self, bucket_name, lifecycle=DEFAULT_LIFECYCLE):
    bucket = self.conn.create_bucket(bucket_name)
    bucket.configure_lifecycle(lifecycle)
    return bucket

  def lookup_bucket(self, bucket_name):
    return self.conn.lookup(bucket_name)
  
  def get_bucket(self, bucket_name):
    return self.conn.get_bucket(bucket_name)
  
  def write_key(self, bucket, key_name, fp, metadata):
    key = Key(bucket)
    key.key = key_name
    key.set_contents_from_string(fp.read())
    for k,v in metadata.items():
      key.set_metadata(k, v)
  
  def disconnect(self):
    self.logger.info('Disconnecting from %s' % self.conn.host)
    self.conn.close()