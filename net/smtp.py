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

from email.mime.text import MIMEText
import logging
import smtplib


class SmtpClient():
  def __init__(self, host='', port=0, username='', password=''):
    self.logger = logging.getLogger('SmtpClient')
    self.host = host
    self.port = port
    self.username = username
    self.password = password

  def connect(self):
    self.logger.info('Connecting to %s:%d' % (self.host, self.port))
    self.smtp = smtplib.SMTP(self.host, self.port)
    self.smtp.starttls()
    self.smtp.login(self.username, self.password)
    
  def send_message(self, from_addr, to_addrs, message, subject=''):
    mime_text = MIMEText(message)
    mime_text['Subject'] = subject
    mime_text['From'] = from_addr
    self.smtp.sendmail(from_addr, to_addrs, mime_text.as_string())
    
  def disconnect(self):
    self.logger.info('Disconnecting from %s:%d', self.host, self.port)
    self.smtp.quit()
    
if __name__ == '__main__':
  smtp_client = SmtpClient('smtp.gmail.com', 587, username='tfbeatty', password='R@ckC1ty!')
  smtp_client.connect()
  message = 'Test message'
  try:
    smtp_client.send_message('tfbeatty@gmail.com.', 'tfbeatty@gmail.com', message, 'tests')
  finally:
    smtp_client.disconnect()
  
