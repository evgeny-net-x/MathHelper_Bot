#include "main.h"

size_t ParseInt(char *buffer, int64_t *num)
{
	assert(buffer && num);

	size_t i = 0;
	*num = 0;

	while (buffer[i]) {
		if (buffer[i] < '0' || buffer[i] > '9')
			break;

		*num = *num*10 + buffer[i]-'0';
		i++;
	}

	return i;
}

size_t ParseFloat(char *buffer, double *num)
{
	assert(buffer && num);

	int i = 0;
	int length = 0;
	int num_is_neg = 0;
	int64_t integer;

	if (buffer[i] == '-') {
		num_is_neg = 1;
		i++;
	}

	length = ParseInt(buffer+i, &integer);
	*num = (double) integer;
	i += length;
	if (length == 0)
		goto Format_Error;

	if (buffer[i] == '.') {
		i++;

		double mantissa;
		length = ParseInt(buffer+i, &integer);
		mantissa = (double) integer;

		i += length;
		if (length == 0)
			goto Format_Error;

		while (length != 0) {
			mantissa /= 10.0;
			length--;
		}

		*num += mantissa;
	}

	if (buffer[i] == 'e' || buffer[i] == 'E') {
		int e_is_neg = 0;
		i++;

		if (buffer[i] == '-')
			e_is_neg = 1;
		else if (buffer[i] != '+')
			goto Format_Error;
		i++;

		int64_t e;
		length = ParseInt(buffer+i, &e);
		i += length;
		if (length == 0)
			goto Format_Error;

		if (e_is_neg)
			while (e-- != 0) *num /= 10.0;
		else
			while (e-- != 0) *num *= 10.0;
	}

	if (num_is_neg)
		*num = -*num;

	return i;
	Format_Error:
		return 0;
}

void ParsePage(char *buffer, Page *page)
{
	assert(buffer && page);

	int length = ParseFloat(buffer, &page->begin);
	buffer += length;

	if (buffer[0] == '\n')
		page->end = page->begin;
	else {
		buffer++;
		ParseFloat(buffer, &page->end);
	}
}

Telebot *Telebot_New(char *token_path, char *socks_url)
{
	assert(token_path);

	FILE *token_file = fopen(token_path, "r");
	if (!token_file)
		goto Open_Error;

	char token[TOKEN_SIZE] = {0};
	if (!fgets(token, TOKEN_SIZE, token_file))
		goto Read_Error;

	token[strlen(token)-1] = '\0';
	fclose(token_file);

	telebot_handler_t handle;
	if (telebot_create(&handle, token) != TELEBOT_ERROR_NONE)
		goto Create_Error;

	if (socks_url && telebot_set_proxy(handle, socks_url, NULL))
		goto SetProxy_Error;

	Telebot *this = malloc(sizeof(Telebot));
	if (!this)
		goto Alloc_Error;

	*this = (Telebot) {
		.handle = handle
	};

	return this;
	Alloc_Error:
	SetProxy_Error:
		telebot_destroy(handle);
	Create_Error:
	Read_Error:
		fclose(token_file);
	Open_Error:
		return NULL;
}

void Telebot_Delete(Telebot *this)
{
	assert(this);

	telebot_destroy(this->handle);
	free(this);
}

int Compare_func(void *a, void *b)
{
	double key = *(double *) a;
	Page *page = (Page *) b;

	if (key < page->begin)
		return -1;
	else if (page->end < key)
		return 1;
	else
		return 0;
}

int Telebot_Update(Telebot *this, Page *pages, int pages_count)
{
	int count, offset = 1;
	char str[4096];
	double task_num = 0.0;
	telebot_error_e ret;
	telebot_message_t message;

	while (1) {
		telebot_update_t *updates;

		ret = telebot_get_updates(this->handle, offset, 20, 0, NULL, 0, &updates, &count);
		if (ret != TELEBOT_ERROR_NONE)
			continue;

		printf("Number of updates: %d\n", count);

		for (int i = 0; i < count; i++) {
			message = updates[i].message;
			printf("=======================================================\n");
			printf("%s: %s \n", message.from->first_name, message.text);

			int length = ParseFloat(message.text, &task_num);

			if (strcmp(message.text, "/start") == 0) {
				snprintf(str, SIZE_OF_ARRAY(str), "Hello %s", message.from->first_name);
				ret = telebot_send_message(this->handle, message.chat->id, str, "", false, false, 0, "");
			} else if (length > 0 && message.text[length] == '\0') {
				Page *page = bsearch(&task_num, pages, pages_count, sizeof(Page), Compare_func);
				int page_num = (((size_t) page- (size_t) pages) / sizeof(Page));

				snprintf(str, SIZE_OF_ARRAY(str), "./Book_files/Math_page%d%s", page_num, ".pdf");
				ret = telebot_send_document(this->handle, message.chat->id, str, 1, 0, 0, NULL);
			} else {
				snprintf(str, SIZE_OF_ARRAY(str), "You have to enter float/integer number");
				ret = telebot_send_message(this->handle, message.chat->id, str, "", false, false, 0, "");
			}

			if (ret != TELEBOT_ERROR_NONE)
				printf("Failed to send message: %d \n", ret);

			offset = updates[i].update_id + 1;
		}

		telebot_free_updates(updates, count);
	}
}

int main(int argc, char **argv)
{
	int i;
	char buffer[20] = {0};
	Page pages[455] = {{0}};
	FILE *file = fopen("./Book_files/Math_pages.txt", "r");
	if (!file)
		goto Open_Error;

	for (i = 0; fgets(buffer, 20, file); i++)
		ParsePage(buffer, pages+i);

	Telebot *bot = Telebot_New(".token", "socks://127.0.0.1:9050");
	if (!bot)
		goto New_Error;

	Telebot_Update(bot, pages, i+1);
	Telebot_Delete(bot);

	return 0;
	New_Error:
		fclose(file);
	Open_Error:
		return 1;
}


