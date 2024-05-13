FROM postgres:14.9

COPY api_readstash/scripts/postgres /usr/local/bin/temp
RUN chmod +x /usr/local/bin/temp/* && \
    mv /usr/local/bin/temp/* /usr/local/bin &&  \
    rmdir /usr/local/bin/temp

COPY docker/postgres_readstash/entrypoint_readstash.sh /usr/local/bin/

ENTRYPOINT ["entrypoint_readstash.sh"]
CMD ["postgres"]