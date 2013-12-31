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

from mockito import any, mock, verify, when

from system.activity import RetryingActivity, ActivityRunner, DeliveryActivity


class ActivityTests(unittest.TestCase):
  def setUp(self):
    logging.basicConfig()
  
  def testDeliveryActivity(self):
    mock_writer = mock()
    mock_data_source = mock()
    metadata = {}
    activity = DeliveryActivity(mock_data_source, mock_writer, metadata)
    activity.start()
    verify(mock_data_source).get_reader()
    verify(mock_writer).write(any(), any())
    
  def testRetryingActivity(self):
    mock_delegate = mock()
    when(mock_delegate).start().thenRaise(Exception('Simulated exception'))
    activity = RetryingActivity(mock_delegate)
    try:
      activity.start()
    except: 
      pass
    verify(mock_delegate, times=3).start()

  def testActivityRunnerSuccess(self):
    mock_activity = mock()
    mock_success_handler = mock()
    mock_failure_handler = mock()
    ActivityRunner(mock_activity, mock_success_handler, mock_failure_handler).run()
    verify(mock_success_handler).handle_success(any())
    verify(mock_failure_handler, times=0).handle_failure(any(), any())
    
  def testActivityRunnerFailure(self):
    mock_activity = mock()
    when(mock_activity).start().thenRaise(Exception('Simulated exception'))
    mock_success_handler = mock()
    mock_failure_handler = mock()
    ActivityRunner(mock_activity, mock_success_handler, mock_failure_handler).run()
    verify(mock_success_handler, times=0).handle_success()
    verify(mock_failure_handler).handle_failure(any(), any())
    
  def testActivityRunnerRetry(self):
    mock_delegate = mock()
    when(mock_delegate).start().thenRaise(Exception('Simulated exception'))
    activity = RetryingActivity(mock_delegate)
    mock_success_handler = mock()
    mock_failure_handler = mock()
    ActivityRunner(activity, mock_success_handler, mock_failure_handler).run()
    verify(mock_success_handler, times=0).handle_success(any())
    verify(mock_failure_handler).handle_failure(any(), any())
    
