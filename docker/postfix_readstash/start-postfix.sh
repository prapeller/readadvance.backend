#!/bin/bash

# Set DNS servers
echo "nameserver 8.8.8.8" > /etc/resolv.conf
echo "nameserver 1.1.1.1" >> /etc/resolv.conf

nslookup mail.ru
dig mail.ru MX
host mail.ru

# Start Postfix in the foreground
postfix start-fg