P=main
SRC_FILES=$(shell find . -type f -name *.c)
OBJ_FILES=$(SRC_FILES:.c=.o)

CFLAGS=-c -g -O3 -Wall -Wno-unused-function
LFLAGS=-ltelebot
CC=gcc

all: $(SRC_FILES) $(P)
.c.o:
	$(CC) $(CFLAGS) $< -o $@
$(P): $(OBJ_FILES)
	$(CC) $(OBJ_FILES) $(LFLAGS) -o $(P)
clean:
	rm $(OBJ_FILES)
	rm $(P)
