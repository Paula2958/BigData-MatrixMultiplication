CC=gcc
CFLAGS=-O2 -std=c11 -Wall -Wextra -fopenmp -fno-tree-vectorize
LDLIBS=-lm

all: matrix

matrix: src/matrix.c
	$(CC) $(CFLAGS) $< -o $@ $(LDLIBS)

test: matrix
	./matrix --test

clean:
	rm -f matrix

.PHONY: all test clean
