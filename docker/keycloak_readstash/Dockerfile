FROM quay.io/keycloak/keycloak:24.0.3

COPY ./docker/keycloak_readstash/entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["start"]
