# data-distribution

This project is a demo I did for a job application several years ago involving generic distribution of data. It can integrate with any data source and can easily be extended to support sophisticated use cases.

The domain is modeled by a small set of generic objects:

* *activities* - the basic units of work
* *data sources* - provide data to activities
* *writers* - entities to which activities can write data

Using these entities it is easy to implement various workflows, for example: 

> once every day, render customer data, deliver it to Amazon S3, and send an email 
> notification containing a link to the file

## Data Sources

Data sources are represented using the [datasource](https://pypi.python.org/pypi/datasource/0.1.0) Python module. It is a simple wrapper for fetching data that provides a uniform interface and supports reading from various sources:

	# From an in-memory string
    data = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    ds = DataSource(data)
    
    # From a file
    filepath = '/home/user/afile.txt'
	ds = DataSource(filepath)
    
    # From a url
    url = 'https://github.com/tbeatty/data-distribution/blob/master/README.md'
    ds = DataSource(url)
    
    # From a function
    f = lambda: return 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    ds = datasource.DataSource(f)
    
Reading from a `DataSource` is easy:

    reader = ds.get_reader()
	print reader.read()	


## Activities

An `Activity` is an object that represents a unit of work. It can be provided some `metadata` and is started up by calling `start()`.

	class Activity:
	  def __init__(self, metadata={}):
	    self.metadata = metadata
	    
	  def start(self):
	    pass
	    
A `DeliveryActivity` extends the basic `Activity`. In addition to some `metadata`, it also uses a `DataSource` and a `FileWriter`. When started up, it simply reads from the data source and writes to the writer.

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
	      
An `ActivityRunner` can be used to run activities when it is necessary to handle success and failure events.

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
          
The default activity success and failure handlers just log the event, but handlers that send email notifications are also included.

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


## Delivery to S3

Amazon S3 is an online cloud storage system from Amazon Web Services. It is highly scalable, has configurable access control, and provides a language-neutral web services interface.

Interacting with S3 is easy with the Amazon Web Services client for Python [boto](https://github.com/boto/boto). 

    class S3Client():
      def __init__(self, access_key_id=None, secret_access_key=None):
        self.logger = logging.getLogger('S3Client')
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key
        
      def connect(self):
        self.conn = boto.connect_s3(self.access_key_id, self.secret_access_key)
        self.logger.info('Connected to %s' % self.conn.host)
      
      def write_key(self, bucket, key_name, fp, metadata):
        key = Key(bucket)
        key.key = key_name
        key.set_contents_from_string(fp.read())
        for k,v in metadata.items():
          key.set_metadata(k, v)


An `S3Client` can be used with an `S3FileWriter` to deliver data from a `DeliveryActivity` to Amazon S3.

    writer = S3FileWriter(S3_CLIENT)
  	data_source = DataSource(RandomDataGenerator().get_random_data)
  	uuid = uuid4()
  	metadata = {'title': 'S3 example',
    	        'generated-by': os.getlogin(),
        	    'bucket': 'tfbeatty-s3-example',
            	'key': str(uuid),
              	'uuid': str(uuid),
              	'timestamp': datetime.utcnow().isoformat()}
    activity = DeliveryActivity(data_source, writer, metadata)

## Delivery to FTP

An on-site ftp server can be a simple and cost effective service for file distribution. A simple ftp client can be implemented with ftplib. 

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

An `FtpClient` can be used with an `FtpFileWriter` to deliver data to an ftp server.

    data_source = DataSource(RandomDataGenerator().get_random_data)
    uuid = uuid4()
    metadata = {'title': 'Ftp document', 
                'generated-by': os.getlogin(),
                'filename': '/opt/example/%s' % str(uuid),
                'uuid': str(uuid),
                'timestamp': datetime.utcnow().isoformat()}
    activity = DeliveryActivity(data_source, FtpFileWriter(FTP_CLIENT), metadata)


## Fault tolerance

In some cases, an `Activity` must tolerate failure scenarios. Retrying a failed activity is handled by wrapping the activity with a `RetryingActivity`.

    writer = S3FileWriter(S3_CLIENT)
    data_source = DataSource(RandomDataGenerator().get_random_data)
	uuid = uuid4()
	metadata = {'title': 'S3 example',
		        'generated-by': os.getlogin(),
				'bucket': 'tfbeatty-s3-example',
				'key': str(uuid),
				'uuid': str(uuid),
				'timestamp': datetime.utcnow().isoformat()}
    activity = RetryingActivity(S3DeliveryActivity(data_source, writer, metadata))
    
A `RetryingActivity` attempts to run the activity a configurable number of times

    class RetryingActivity(Activity):
      def __init__(self, delegate, metadata={}):
        Activity.__init__(self, metadata)
        self.delegate = delegate
         
      def log_retry(*args, **kwargs):  # @NoSelf
        tries_remaining, ex, delay_sec = args
        logger = logging.getLogger('RetryingActivity')
        logger.warn('Caught exception - %s - %d tries remaining - delaying %d seconds' % 
            (ex, tries_remaining, delay_sec))
       
      @retries(3, exceptions=(Exception,), hook=log_retry)
      def start(self):
        return self.delegate.start()
        
The list of exceptions to retry is customizable.
        
When used with an `ActivityRunner`, the `ActivitySuccessHandler` or `ActivityFailureHandler` is only invoked after the activity has completed successfully or run out of retries.

## Example

As an example, `example/scheduler.py` implements a job scheduling service that does the following:

  * Delivers a dump of random data to Amazon S3 once every hour
  * Delivers a dump of random data to a remote ftp server at midnight on weekdays
  * Notifies users of successful delivery and system admin of failures

The scheduler is implemented by the [Advanced Python Scheduler](http://pythonhosted.org/APScheduler/), which provides

  * Configurable scheduling mechanisms
  * Support for multiple, simultaneously active job stores including RAM, a simple file-based database, any RDBMS, MongoDB, Redis

	      
## Python Libraries

This project requires the following non-standard Python libraries:

* [boto](https://github.com/boto/boto)
* [datasource](https://pypi.python.org/pypi/datasource/0.1.0)
* [apscheduler](http://pythonhosted.org/APScheduler/)
* [PyYAML](https://pypi.python.org/pypi/PyYAML)
* [mockito-python](https://code.google.com/p/mockito-python/)

