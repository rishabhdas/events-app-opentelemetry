all: up bootstrap

up: 
	@docker-compose up -d 

bootstrap:
	@sleep 10
	@python3 bootstrap.py

build: bootstrap
	@docker-compose up --build

down:
	@docker-compose down