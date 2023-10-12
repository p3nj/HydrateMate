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


## 3. Restart the Mosquitto
`sudo systemctl restart mosquitto.service`


## 4. Example Python Code
Please check out the `publisher_test.py` and `subscriber_test.py` for example of using certificate to establish the conneciton.
