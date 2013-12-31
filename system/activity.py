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
import traceback

from system.retry import retries


class Activity:
  def __init__(self, metadata={}):
    self.metadata = metadata
    
  def start(self):
    pass
  
class RetryingActivity(Activity):
  def __init__(self, delegate):
    Activity.__init__(self, delegate.metadata)
    self.delegate = delegate
     
  def log_retry(*args, **kwargs):  # @NoSelf
    tries_remaining, ex, delay_sec = args
    logger = logging.getLogger('RetryingActivity')
    logger.warn('Caught exception - %s - %d tries remaining - delaying %d seconds' % 
        (ex, tries_remaining, delay_sec))
   
  @retries(3, exceptions=(Exception,), hook=log_retry)
  def start(self):
    return self.delegate.start()

class DeliveryActivity(Activity):
  def __init__(self, data_source, writer, metadata={}):
    Activity.__init__(self, metadata)
    self.logger = logging.getLogger('DeliveryActivity')
    self.data_source = data_source
    self.writer = writer
  
  def start(self):
    self.logger.info('Reading data')
    reader = self.data_source.get_reader()
    self.logger.info('Writing data') 
    self.writer.write(reader, self.metadata)

class ActivitySuccessHandler():
  def __init__(self):
    self.logger = logging.getLogger('ActivitySuccessHandler')
    
  def handle_success(self, *args):
    self.logger.info('Activity succeeded')
  
class ActivityFailureHandler():
  def __init__(self):
    self.logger = logging.getLogger('ActivityFailureHandler')
    
  def handle_failure(self, *args):
    self.logger.info('Activity failed')

DEFAULT_ACTIVITY_SUCCESS_HANDLER = ActivitySuccessHandler()
DEFAULT_ACTIVITY_FAILURE_HANDLER = ActivityFailureHandler()

class EmailNotifyingActivitySuccessHandler(ActivitySuccessHandler):
  def __init__(self, smtp_client, from_addr, to_addrs, subject='Success notification'):
    self.logger = logging.getLogger('EmailNotifyingActivitySuccessHandler')
    self.smtp_client = smtp_client
    self.from_addr = from_addr
    self.to_addrs = to_addrs
    self.subject = subject
    
  def handle_success(self, metadata):
    self.logger.info('Sending success notification email')
    try:
      self.smtp_client.connect()
      self.smtp_client.send_message(self.from_addr, self.to_addrs, 
          'Success message\n\nMetadata: %s' % metadata, self.subject)
    finally:
      self.smtp_client.disconnect()
    
class EmailNotifyingActivityFailureHandler(ActivityFailureHandler):
  def __init__(self, smtp_client, from_addr, to_addrs, subject='Failure notification'):
    self.logger = logging.getLogger('EmailNotifyingActivityFailureHandler')
    self.smtp_client = smtp_client
    self.from_addr = from_addr
    self.to_addrs = to_addrs
    self.subject = subject
    
  def handle_failure(self, ex, metadata):
    self.logger.info('Sending failure notification email')
    try:
      self.smtp_client.connect()
      self.smtp_client.send_message(self.from_addr, self.to_addrs, 
          'Failure message\n\nException: %s:%s\nStack trace: %s\nMetadata: %s' % 
          (type(ex), ex, traceback.format_exc(ex), metadata), self.subject)
    finally:
      self.smtp_client.disconnect()

class ActivityRunner():
  def __init__(self, activity, success_handler=DEFAULT_ACTIVITY_SUCCESS_HANDLER, 
               failure_handler=DEFAULT_ACTIVITY_FAILURE_HANDLER):
    self.logger = logging.getLogger('ActivityRunner')
    self.activity = activity
    self.success_handler = success_handler
    self.failure_handler = failure_handler
  
  def run(self):
    try:
      self.activity.start()
    except Exception as ex:
      self.logger.exception(ex)
      self.failure_handler.handle_failure(ex, self.activity.metadata)
    else:
      self.success_handler.handle_success(self.activity.metadata)
    
