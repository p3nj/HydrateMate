# TLS Connection Setup Guide

## 1. Setup the Directories.
### Certs
`sudo mkdir -p /etc/mosquitto/certs` 
### Storage
`sudo mkdir -p /var/lib/mosquitto`
### Logs
`sudo mkdir -p /var/log/mosquitto`
`sudo touch /var/log/mosquitto/mosquitto.log`

### Change the Owner Ship to Mosquitto
`sudo chown -R mosquitto:mosquitto /etc/mosquitto/certs`

`sudo chown -R mosquitto:mosquitto /var/lib/mosquitto`

`sudo chown -R mosquitto:mosquitto /var/log/mosquitto`

## 2. CA Certificates
You can definely try to create this by yourself, not recommanded, though.

Because it's shitty process for self-signed CA and certificate creation.

I don't have the tutorial here, if you planned to do it good luck.

### Download Pre-Made Certificate
#### Change the working directory
`cd /etc/mosquitto/certs/`
#### Download the certificate from my lovely develop server
`sudo wget https://hm-p3nj.wunderbucket.dev/certs/certs_latest.zip` 
#### Unzip the certificate
`sudo unzip certs_latest.zip`

## 3. Update Mosquitto Configuration
Firstly, backup the origional config file, incase you fucked up and cannot revert.

`sudo mv /etc/mosquitto/mosquitto.conf /etc/mosquitto/mosquitto.conf.bak`

Second, create a new config file with the content below

`sudo touch /etc/mosquitto/mosquitto.conf`

Lastly, after create the file, use your favorite editor to paste the config below into the file.

```
# General settings
pid_file /var/run/mosquitto.pid
persistence true
persistence_location /var/lib/mosquitto/

# Logging
log_dest file /var/log/mosquitto/mosquitto.log
log_type all

# Default stener
listener 1883 localhost

# Secure listener
listener 8883

cafile /etc/mosquitto/certs/ca.crt
certfile /etc/mosquitto/certs/server.crt
keyfile /etc/mosquitto/certs/server.key

tls_version tlsv1.2

# Require client certificate
require_certificate true

# Allow Anonymous
allow_anonymous true
```

## 4. Restart the Mosquitto
`sudo systemctl restart mosquitto.service`


## 5. Example Python Code
Please check out the `publisher_test.py` and `subscriber_test.py` for example of using certificate to establish the conneciton.


## Extra
### Monitoring the Mosquitto Process
Because we setup a log file `/var/log/mosquitto/mosquitto.log`, you can monitor the mosquitto by using the command:

`tail -F /var/log/mosquitto/mosquitto.log`

### Encryption Example
Checkout the example script `publisher_crc.py` and `subscriber_crc.py`, it's messy, I will try to prettify it later.

Here are the example output from the `subscriber_crc.py`
```
Received message on topic: mate/hello
Message payload: b'P\x16^^\x7fZG\x0cb\xf35\xe3\x84\xe1\xbc\xf3\xf8\x0b\x8a\x81\xa7\xe1[QC \xcf\xc3-\x14\xedo<\x8f\xe6\x85\n+\xd9Y\xb2\xe5\xca\xf4W%BEj\x7fyl\r"\x8f\x9ab\xe1\xb0\x15\xeaV\x86\xe3\x83\xdf\xf4\x99\x029\x05\x93\xa5\xda\x14\xbd\xef\xd9\xd4\xa1uW\x01:*\x13&q\x0f\xd3\x12?,\x00k\x954h5\xc7yb\xc8\x8c$\xa2\xd6q\xda\xd0\xc0\xf3\xa6:xM\\\xd7\xb2|\xa9.[=\x8e,2\xa3T\x00\xc9\xf8?\xb6\xdfG\xa2\x05\'\x1a,\xe1UYS\xc7\x9e\x13\xd7\x94B6M\xf8[\x8d\x1f\xa4\xf3p\x1f\xb8W\xa9\x90>\xf1k\xbc\xafX\xf0\xe1\xec\x15\xc5\xed\xe0\xf3\xba\x98\x86MZ\x98ot\xae\xe7\xb3\x1b\x17\xbd:\xf3\x08\xed_R\xef\x82\xf9\xcf\xe9\xfa\x98\x8c\x11\xac-\xcfk\xfaX7,*\x1a&\x88nK\x17\x93\xc6|d\xe1\x99A\xe5\x10\xc3e\x16Ji~\x12~<U\xa4\xac\xd5U\x0b\xe6\xf2\xeeW\'jk\x9ak'
Decrypted data: {'data': {'event_time': '2023-10-12T12:17:03.615Z', 'weight': 'str'}, 'crc': '3956316572'}
CRC Verification: Data is valid.
Received message on topic: mate/hello
Message payload: b'\x82<\x15\x92\x80\xb5Si\xde\x1e\x1ci\xeb\t\xe2\xb2+\xf0lGu;\x8e\xe8.F[`\xe6a\x9d7\x03%\xec\x1c*\x1azg\x83\\\xfb&\x1e\x1f\xe9\xa5\x078iC\x82\x8b\x1eS\x99j\xd6\xf3\xed\xd0\x9c\xdch+\x89\xe0\xc8P\xd7X\x19\x89sY\x8b\x8a+\xb6\xfc\x97\xa7N+\xa5\x96\xd0w\xb6\xce\xcc\x8e\xe8\xe7[\xb0\xbf\xf7:\x9d\xb1\x16\x80\x05A\xbf#\xff\xb6<\xbc6\xe8^2"\xfcB\x9c\t\x07\nN.\xbe\x03\xad\xc06\xbe\xee\xd2\xb0EJ\xd7\x1f\x19G\xfb\xef\x113\x8aGe\x1c\x9f}\xf0\xcb\xe35\xf0\xfa\x86T\x83\xa0\xc3\x9e\x16\xafV\x95*|\xa5Mh\xcc\x84\x8d\xbc\xb0\xb9\xb1\xf0\x13\x1a0s5\x94\xd3\xff\x1c\xce\x1c\xd2X\xe1;\xb9\xe7\x91\xc6\x9d\x89nP\x93\x14Z4\x15?| \xed_N\xc1\xc1g\x10d\xc0\xa2o\xc93b\xed\x8df\xc7/(\xf2\x81\x95E%\\p\x0e\t8\x06 \xcc@\xbd\x9d\xb0A\xe5\xb7v\xa0\x98\x87\x10\xdb'
Decrypted data: {'data': {'event_time': '2023-10-12T12:17:04.618Z', 'weight': 'str'}, 'crc': '2370956135'}
CRC Verification: Data is valid.
```


Have fun.
