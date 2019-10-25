# S3 Wrapper

Provide simple functions for interacting with an S3 Bucket.

You must create an `s3_config.py` file, with login credentials, and bucket. See Arik for details.


### Examples

```python3
from s3_class import S3


# Create an S3 object and set current workind directory if desired
s = S3('ED')

# Upload file located at URL to desired directory
s.uploadWithURL('production_files', data_url)

# Upload base64 encoded data to desired directory
s.uploadWithBase64('screenshots', 'example_base64.png', data_base64)

# Upload local file to desired directory
with open('/path/to/file', 'rb') as data_binary:
    s.uploadWithBinary('screenshots', 'example_binary.png', data_binary)
```
