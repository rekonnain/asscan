build:
	docker-compose build

clean: stop
	docker rmi -f $(docker images -a -q)
	docker image prune -a
	docker volume prune

stop:
	docker-compose down

kill:
	sh -c 'docker rm -f $(docker ps -a -q)'

run: stop build
	docker-compose up

