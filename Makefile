all: start_python

build_python:
	docker build -t vkparser:python -f ./Dockerfile_python .

start_python: build_python
	docker run -it --rm -v `pwd`:/mnt -w /mnt \
		vkparser:python \
		python main.py
