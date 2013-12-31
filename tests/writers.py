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
import unittest

from mockito import any, mock, verify

from system.writer import FtpFileWriter, S3FileWriter


class WriterTests(unittest.TestCase):
  def setUp(self):
    logging.basicConfig()
  
  def testFtpFileWriter(self):
    mock_ftp_client = mock()
    writer = FtpFileWriter(mock_ftp_client)
    writer.write(mock(), {'filename': 'test'})
    verify(mock_ftp_client).connect()
    verify(mock_ftp_client).write_file(any(), any())
    verify(mock_ftp_client).disconnect()

  def testS3FileWriter(self):
    mock_s3_client = mock()
    writer = S3FileWriter(mock_s3_client)
    writer.write(mock(), {'bucket': 'test bucket', 'key': 'test key'})
    verify(mock_s3_client).connect()
    verify(mock_s3_client).write_key(any(), any(), any(), any())
    verify(mock_s3_client).disconnect()  
