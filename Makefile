API_READSTASH_BASE := -f ./docker/api_readstash/docker-compose-base.yml
API_READSTASH_LOCAL := -f ./docker/api_readstash/docker-compose-local.yml
API_READSTASH_PROD := -f ./docker/api_readstash/docker-compose-prod.yml

API_NLP_BASE := -f ./docker/api_nlp/docker-compose-base.yml
API_NLP_LOCAL := -f ./docker/api_nlp/docker-compose-local.yml
API_NLP_PROD := -f ./docker/api_nlp/docker-compose-prod.yml

POSTGRES_READSTASH_BASE := -f ./docker/postgres_readstash/docker-compose-base.yml
POSTGRES_READSTASH_LOCAL := -f ./docker/postgres_readstash/docker-compose-local.yml
POSTGRES_READSTASH_PROD := -f ./docker/postgres_readstash/docker-compose-prod.yml

PROM_GRAF_BASE := -f ./docker/prometheus_grafana/docker-compose-base.yml
PROM_GRAF_LOCAL := -f ./docker/prometheus_grafana/docker-compose-local.yml
PROM_GRAF_PROD := -f ./docker/prometheus_grafana/docker-compose-prod.yml

KEYCLOAK_BASE := -f ./docker/keycloak_readstash/docker-compose-base.yml
KEYCLOAK_LOCAL := -f ./docker/keycloak_readstash/docker-compose-local.yml
KEYCLOAK_PROD := -f ./docker/keycloak_readstash/docker-compose-prod.yml

REDIS_READSTASH_BASE := -f ./docker/redis_readstash/docker-compose-base.yml
REDIS_READSTASH_LOCAL := -f ./docker/redis_readstash/docker-compose-local.yml
REDIS_READSTASH_PROD := -f ./docker/redis_readstash/docker-compose-prod.yml

POSTFIX_READSTASH_BASE := -f ./docker/postfix_readstash/docker-compose-base.yml
POSTFIX_READSTASH_LOCAL := -f ./docker/postfix_readstash/docker-compose-local.yml
POSTFIX_READSTASH_PROD := -f ./docker/postfix_readstash/docker-compose-prod.yml

RABBITMQ_READSTASH_BASE := -f ./docker/rabbitmq_readstash/docker-compose-base.yml
RABBITMQ_READSTASH_LOCAL := -f ./docker/rabbitmq_readstash/docker-compose-local.yml
RABBITMQ_READSTASH_PROD := -f ./docker/rabbitmq_readstash/docker-compose-prod.yml


build-loc:
	docker network create shared_network || true
	docker-compose -p keycloak_readstash $(KEYCLOAK_BASE) $(KEYCLOAK_LOCAL) up --build -d --remove-orphans
	docker-compose -p postgres_readstash $(POSTGRES_READSTASH_BASE) $(POSTGRES_READSTASH_LOCAL) up --build -d --remove-orphans
	docker-compose -p api_readstash $(API_READSTASH_BASE) $(API_READSTASH_LOCAL) up --build -d --remove-orphans
	docker-compose -p api_nlp $(API_NLP_BASE) $(API_NLP_LOCAL) up --build -d --remove-orphans
	docker-compose -p redis_readstash $(REDIS_READSTASH_BASE) $(REDIS_READSTASH_LOCAL) up --build -d --remove-orphans
	docker-compose -p rabbitmq_readstash $(RABBITMQ_READSTASH_BASE) $(RABBITMQ_READSTASH_LOCAL) up --build -d --remove-orphans

down-loc:
	docker-compose -p keycloak_readstash $(KEYCLOAK_BASE) $(KEYCLOAK_LOCAL) down
	docker-compose -p postfix_readstash $(POSTFIX_READSTASH_BASE) $(POSTFIX_READSTASH_LOCAL) down
	docker-compose -p postgres_readstash $(POSTGRES_READSTASH_BASE) $(POSTGRES_READSTASH_LOCAL) down
	docker-compose -p api_readstash $(API_READSTASH_BASE) $(API_READSTASH_LOCAL) down
	docker-compose -p api_nlp $(API_NLP_BASE) $(API_NLP_LOCAL) down
	docker-compose -p redis_readstash $(REDIS_READSTASH_BASE) $(REDIS_READSTASH_LOCAL) down
	docker-compose -p rabbitmq_readstash $(RABBITMQ_READSTASH_BASE) $(RABBITMQ_READSTASH_LOCAL) down

down-v-loc:
	docker-compose -p keycloak_readstash $(KEYCLOAK_BASE) $(KEYCLOAK_LOCAL) down -v
	docker-compose -p postfix_readstash $(POSTFIX_READSTASH_BASE) $(POSTFIX_READSTASH_LOCAL) down -v
	docker-compose -p postgres_readstash $(POSTGRES_READSTASH_BASE) $(POSTGRES_READSTASH_LOCAL) down -v
	docker-compose -p api_readstash $(API_READSTASH_BASE) $(API_READSTASH_LOCAL) down -v
	docker-compose -p redis_readstash $(REDIS_READSTASH_BASE) $(REDIS_READSTASH_LOCAL) down -v



build-prod:
	docker network create shared_network || true
	docker-compose -p keycloak_readstash $(KEYCLOAK_BASE) $(KEYCLOAK_LOCAL) build
	docker-compose -p postgres_readstash $(POSTGRES_READSTASH_BASE) $(POSTGRES_READSTASH_PROD) build
	docker-compose -p api_readstash $(API_READSTASH_BASE) $(API_READSTASH_PROD) build
	docker-compose -p redis_readstash $(REDIS_READSTASH_BASE) $(REDIS_READSTASH_PROD) build

run-prod:
	docker network create shared_network || true
	docker-compose -p keycloak_readstash $(KEYCLOAK_BASE) $(KEYCLOAK_LOCAL) up -d --remove-orphans
	docker-compose -p postgres_readstash $(POSTGRES_READSTASH_BASE) $(POSTGRES_READSTASH_PROD) up -d --remove-orphans
	docker-compose -p api_readstash $(API_READSTASH_BASE) $(API_READSTASH_PROD) up -d --remove-orphans
	docker-compose -p redis_readstash $(REDIS_READSTASH_BASE) $(REDIS_READSTASH_PROD) up -d --remove-orphans

down-prod:
	docker-compose -p keycloak_readstash $(KEYCLOAK_BASE) $(KEYCLOAK_LOCAL) down
	docker-compose -p postgres_readstash $(POSTGRES_READSTASH_BASE) $(POSTGRES_READSTASH_PROD) down
	docker-compose -p api_readstash $(API_READSTASH_BASE) $(API_READSTASH_PROD) down
	docker-compose -p redis_readstash $(REDIS_READSTASH_BASE) $(REDIS_READSTASH_PROD) down

down-v-prod:
	docker-compose -p keycloak_readstash $(KEYCLOAK_BASE) $(KEYCLOAK_LOCAL) down -v
	docker-compose -p postgres_readstash $(POSTGRES_READSTASH_BASE) $(POSTGRES_READSTASH_PROD) down -v
	docker-compose -p api_readstash $(API_READSTASH_BASE) $(API_READSTASH_PROD) down -v
	docker-compose -p redis_readstash $(REDIS_READSTASH_BASE) $(REDIS_READSTASH_PROD) down -v



keycloak-readstash-build-loc:
	docker network create shared_network || true
	docker-compose -p postgres_readstash $(POSTGRES_READSTASH_BASE) $(POSTGRES_READSTASH_LOCAL) up --build -d --remove-orphans
	docker-compose -p keycloak_readstash $(KEYCLOAK_BASE) $(KEYCLOAK_LOCAL) up --build -d --remove-orphans

keycloak-readstash-down-loc:
	docker network create shared_network || true
	docker-compose -p postgres_readstash $(POSTGRES_READSTASH_BASE) $(POSTGRES_READSTASH_LOCAL) down
	docker-compose -p keycloak_readstash $(KEYCLOAK_BASE) $(KEYCLOAK_LOCAL) down

keycloak-readstash-down-v-loc:
	docker network create shared_network || true
	docker-compose -p postgres_readstash $(POSTGRES_READSTASH_BASE) $(POSTGRES_READSTASH_LOCAL) down -v
	docker-compose -p keycloak_readstash $(KEYCLOAK_BASE) $(KEYCLOAK_LOCAL) down -v



api-readstash-build-loc:
	docker network create shared_network || true
	docker-compose -p api_readstash $(API_READSTASH_BASE) $(API_READSTASH_LOCAL) up --build -d --remove-orphans

api-readstash-down-loc:
	docker-compose -p api_readstash $(API_READSTASH_BASE) $(API_READSTASH_LOCAL) down



api-nlp-build-loc:
	docker network create shared_network || true
	docker-compose -p api_nlp $(API_NLP_BASE) $(API_NLP_LOCAL) up --build -d --remove-orphans

api-nlp-down-loc:
	docker-compose -p api_nlp $(API_NLP_BASE) $(API_NLP_LOCAL) down



postfix-readstash-build-loc:
	docker network create shared_network || true
	docker-compose -p postfix_readstash $(POSTFIX_READSTASH_BASE) $(POSTFIX_READSTASH_LOCAL) up --build -d --remove-orphans

postfix-readstash-down-loc:
	docker-compose -p postfix_readstash $(POSTFIX_READSTASH_BASE) $(POSTFIX_READSTASH_LOCAL) down

postfix-readstash-down-v-loc:
	docker-compose -p postfix_readstash $(POSTFIX_READSTASH_BASE) $(POSTFIX_READSTASH_LOCAL) down -v



redis-readstash-build-loc:
	docker network create shared_network || true
	docker-compose -p redis_readstash $(REDIS_READSTASH_BASE) $(REDIS_READSTASH_LOCAL) up --build -d --remove-orphans

redis-readstash-down-loc:
	docker-compose -p redis_readstash $(REDIS_READSTASH_BASE) $(REDIS_READSTASH_LOCAL) down



rabbit-readstash-build-loc:
	docker network create shared_network || true
	docker-compose -p rabbitmq_readstash $(RABBITMQ_READSTASH_BASE) $(RABBITMQ_READSTASH_LOCAL) up --build -d --remove-orphans

rabbit-readstash-down-loc:
	docker-compose -p rabbitmq_readstash $(RABBITMQ_READSTASH_BASE) $(RABBITMQ_READSTASH_LOCAL) down



postgres-readstash-build-loc:
	docker network create shared_network || true
	docker-compose -p postgres_readstash $(POSTGRES_READSTASH_BASE) $(POSTGRES_READSTASH_LOCAL) up --build -d --remove-orphans

postgres-readstash-down-loc:
	docker-compose -p postgres_readstash $(POSTGRES_READSTASH_BASE) $(POSTGRES_READSTASH_LOCAL) down

postgres-readstash-down-v-loc:
	docker-compose -p postgres_readstash $(POSTGRES_READSTASH_BASE) $(POSTGRES_READSTASH_LOCAL) down -v




api-readstash-inspect-ip:
	docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' api_readstash

postgres-readstash-inspect-ip:
	docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' postgres_readstash
