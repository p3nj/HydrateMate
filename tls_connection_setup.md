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

Have fun.
