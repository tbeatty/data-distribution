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

from datetime import datetime
import logging.config
import os
from uuid import uuid4

from apscheduler.scheduler import Scheduler
from datasource.api import DataSource
import yaml

from net.ftp import FtpClient
from net.s3 import S3Client
from net.smtp import SmtpClient
from system.activity import RetryingActivity, \
  EmailNotifyingActivitySuccessHandler, EmailNotifyingActivityFailureHandler, \
  ActivityRunner, Activity, DeliveryActivity
from system.writer import S3FileWriter, FtpFileWriter


class RandomDataGenerator:
  def __init__(self):
    self.logger = logging.getLogger('RandomDataGenerator')
    
  def get_random_data(self):
    self.logger.info('Generating random data')
    return str(datetime.now()) + '\n'

def s3_activity():
  s3_client = S3Client()
  writer = S3FileWriter(s3_client)
  data_source = DataSource(RandomDataGenerator().get_random_data)
  uuid = uuid4()
  metadata = {'title': 'S3 example',
              'generated-by': os.getlogin(),
              'bucket': 'tfbeatty-s3-example',
              'key': str(uuid),
              'uuid': str(uuid),
              'timestamp': datetime.utcnow().isoformat()}
  activity = RetryingActivity(DeliveryActivity(data_source, writer, metadata))
  smtp_client = SmtpClient('smtp.gmail.com', 587, username='username', password='password')
  from_addr, to_addrs = 'user@example.org', 'admin@example.org'
  success_handler = EmailNotifyingActivitySuccessHandler(smtp_client, from_addr, to_addrs)
  failure_handler = EmailNotifyingActivityFailureHandler(smtp_client, from_addr, to_addrs)
  runner = ActivityRunner(activity, success_handler, failure_handler)
  runner.run()

def ftp_activity():
  data_source = DataSource(RandomDataGenerator().get_random_data)
  ftp_client = FtpClient('localhost', user='username', passwd='password')
  uuid = uuid4()
  metadata = {'title': 'Ftp example', 
              'generated-by': os.getlogin(),
              'filename': '/opt/example/%s' % str(uuid),
              'uuid': str(uuid),
              'timestamp': datetime.utcnow().isoformat()}
  activity = RetryingActivity(DeliveryActivity(data_source, FtpFileWriter(ftp_client), metadata))
  smtp_client = SmtpClient('smtp.gmail.com', 587, username='username', password='password')
  from_addr, to_addrs = 'user@example.org', 'admin@example.org'
  success_handler = EmailNotifyingActivitySuccessHandler(smtp_client, from_addr, to_addrs)
  failure_handler = EmailNotifyingActivityFailureHandler(smtp_client, from_addr, to_addrs)
  runner = ActivityRunner(activity, success_handler, failure_handler)
  runner.run()

def simulate_failure_activity():
  class FailureActivity(Activity):
    def start(self):
      raise Exception()
  smtp_client = SmtpClient('smtp.gmail.com', 587, username='username', password='password')
  from_addr, to_addrs = 'user@example.org', 'admin@example.org'
  failure_handler = EmailNotifyingActivityFailureHandler(smtp_client, from_addr, to_addrs, 
        subject='Simulated Failure Notification')
  runner = ActivityRunner(FailureActivity(), failure_handler=failure_handler)
  runner.run()

if __name__ == '__main__':
  with open('logging.yml') as f:
    config = yaml.load(f)
  logging.config.dictConfig(config)
  scheduler = Scheduler(standalone=True)
  scheduler.add_interval_job(s3_activity, hours=1)
  scheduler.add_cron_job(ftp_activity, hour=0, day_of_week='mon-fri')
  scheduler.add_interval_job(simulate_failure_activity, seconds=5, max_runs=1)
  print('Press Ctrl+C to exit')
  try:
    scheduler.start()
  except (KeyboardInterrupt, SystemExit):
    pass
