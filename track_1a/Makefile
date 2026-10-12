.PHONY: run replay

# Judges run `make run` from the repository root. The root Makefile delegates here.
# Docker is what the challenge asks for. `make replay` is the same check without Docker.
run:
	docker build -t hack-apertus-track1a -f Dockerfile .
	docker run --rm hack-apertus-track1a

replay:
	python src/reproduce.py
