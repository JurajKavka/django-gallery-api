CONTAINER_NAME=gallery_api_test

build:
	docker build --tag gallery_api:latest .

test:
	echo ${PWD}/src:/app

run:
	docker run --name ${CONTAINER_NAME} -it -v ${PWD}/src/:/app/ -p 8000:8000 gallery_api:latest

start:
	docker container start -i ${CONTAINER_NAME}

stop:
	docker container stop ${CONTAINER_NAME}

rm:
	echo "Removing container"
	docker container rm ${CONTAINER_NAME} 

rm-image:
	echo "Removing image from system"
	docker image rm gallery_api:latest
