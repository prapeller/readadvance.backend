# Use an official Ubuntu as a parent image
FROM ubuntu:latest

# Set non-interactive installation to avoid getting stuck on prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install Postfix, Netcat, and other necessary packages
RUN apt-get update && apt-get install -y ca-certificates postfix mailutils netcat-openbsd telnet iputils-ping dnsutils bind9-host && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create the /etc/mailname file
RUN echo "example.com" > /etc/mailname

# Copy your Postfix configuration file into the image
COPY ./docker/postfix_readstash/main.cf /etc/postfix/main.cf
RUN chmod 644 /etc/postfix/main.cf

# Copy the startup script into the image
COPY ./docker/postfix_readstash/start-postfix.sh /usr/local/bin/start-postfix.sh
RUN chmod +x /usr/local/bin/start-postfix.sh

# Expose SMTP port
EXPOSE 25

# Start Postfix using the custom startup script
CMD ["/usr/local/bin/start-postfix.sh"]
