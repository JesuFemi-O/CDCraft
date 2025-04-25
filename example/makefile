.PHONY: build-connect up down logs

build-connect:
	docker buildx build --platform linux/amd64 -t cdcraft/kafka-connect:latest ./kafka-connect --load

up:
	docker compose up -d

down:
	docker compose down -v

logs:
	docker compose logs -f --tail=100

minio-ui:
	open http://localhost:9001

console-ui:
	open http://localhost:8084

connect-status:
	curl http://localhost:8083

connect-plugins:
	curl http://localhost:8083/connector-plugins | jq .

view-connectors:
	curl http://localhost:8083/connectors | jq .

s3-sink:
	curl -i -X POST -H "Accept:application/json" -H "Content-Type:application/json" localhost:8083/connectors/ -d '@./connectors/sink.json'

pg-src:
	curl -i -X POST -H "Accept:application/json" -H "Content-Type:application/json" localhost:8083/connectors/ -d '@./connectors/source.json'