CC = gcc
CFLAGS = -O3 -Wall -Wextra -std=c11 -march=native
LDFLAGS = -lm

TARGET = chess_search
OBJS = main.o board.o minimax.o

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

main.o: main.c board.h minimax.h
	$(CC) $(CFLAGS) -c main.c

board.o: board.c board.h
	$(CC) $(CFLAGS) -c board.c

minimax.o: minimax.c minimax.h board.h
	$(CC) $(CFLAGS) -c minimax.c

clean:
	rm -f $(OBJS) $(TARGET)

run: $(TARGET)
	./$(TARGET) 5 5 2 2 rook

.PHONY: all clean run
