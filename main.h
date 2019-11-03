#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <stdint.h>
#include <string.h>
#include <stdbool.h>
#include <telebot/telebot.h>

#define TOKEN_SIZE 1024
#define SIZE_OF_ARRAY(array) (sizeof(array)/sizeof(array[0]))

typedef struct Page {
	double begin;
	double end;
} Page;

typedef struct Telebot {
	telebot_handler_t handle;
} Telebot;

int Compare_func(void *, void *);
size_t ParseInt(char *, int64_t *);
size_t ParseFloat(char *, double *);
void ParsePage(char *, Page *);
int BinarySearch(int *, int, int);
Telebot *Telebot_New(char *, char *);
void Telebot_Delete(Telebot *);
int Telebot_Update(Telebot *, Page *, int);
