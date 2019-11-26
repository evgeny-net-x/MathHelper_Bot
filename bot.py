import re
import sys
import array
import multiprocessing
import threading
from threading import Thread, BoundedSemaphore
import telebot
from telebot import apihelper, types

class Bot():
	def __init__(self):
		self.pages = []
		self.cpu_count = multiprocessing.cpu_count()
		self.lock = BoundedSemaphore(8*self.cpu_count)
		self.bot = telebot.TeleBot('1043008853:AAFMSGdcbA3l0n9K7fj5xh2dX7Qr1BNWSgw')
		telebot.apihelper.proxy = {'https': 'socks5://127.0.0.1:9050'}
	def getNextPageKeyboard(self, pageNum):
		button = types.InlineKeyboardButton('next page', callback_data="next page " + str(pageNum))
		keyboard = types.InlineKeyboardMarkup()
		keyboard.add(button)
		return keyboard

	def createPages(self, path):
		fd = open(path, "r")

		for line in fd:
			nums = re.findall("[0-9\.]+", line)
			begin= float(nums[0])
			end  = begin

			if len(nums) > 1:
				end = float(nums[1])

			self.pages.append([begin, end])

		fd.close()

	def send_document(self, message, pageNum):
		self.lock.acquire()
		thread = threading.Thread(target=self.__send_document, args=(message, pageNum))
		thread.start()

	def __send_document(self, message, pageNum):
		self.bot.send_document(message.chat.id, open('./Book/Math_page' + str(pageNum) + '.pdf', 'r'), reply_markup=bot.getNextPageKeyboard(pageNum+1))
		self.lock.release()
		sys.exit()

	def send_message(self, message, string):
		self.bot.send_message(message.chat.id, string);

	def findPageNumOfTask(self, task_num):
		begin = 0
		end = len(self.pages)
		mid = end/2

		if not(1 <= task_num and task_num <= self.pages[end-1][1]):
			return -1

		while 1:
			if task_num < self.pages[mid][0]:
				end = mid-1
				mid = (begin+end)/2
			elif self.pages[mid][1] < task_num:
				begin = mid+1
				mid = (begin+end)/2
			else:
				break

		return mid

bot = Bot()

@bot.bot.message_handler(commands=['start'])
def start_message(message):
	bot.send_message(message, 'Hello ' + message.from_user.first_name + '\n/help for additional information')

@bot.bot.message_handler(commands=['help'])
def help_message(message):
	bot.send_message(message, "usage:\n\tnumber - one page with task 'number'")

@bot.bot.callback_query_handler(lambda query: re.match('next page', query.data))
def handle_callback(query):
	pageNum = int(re.findall('[0-9\.]+', query.data)[0])

	if 0 <= pageNum and pageNum < len(bot.pages):
		bot.send_document(query.message, pageNum)
	else:
		bot.send_message(query.message, "There isn't next page");

@bot.bot.message_handler(content_types=['text'])
def send_text(message):
	username = message.from_user.username
	first_name = message.from_user.first_name
	last_name = message.from_user.last_name

	if not username:
		username = "null"
	if not first_name:
		first_name = "null"
	if not last_name:
		last_name = "null"

	print("Message from " + username + " (" + first_name + " " + last_name + "); '" + message.text + "'")

	if not re.match('^[0-9]+(\.[0-9]+)?$', message.text):
		bot.send_message(message, 'You have to enter integer/float number of task')
		return
		
	pageNum = bot.findPageNumOfTask(float(message.text))
	if pageNum == -1:
		bot.send_message(message, "There isn't this task in book!")
		return

	bot.send_document(message, pageNum)

def main():
	bot.createPages("./Book/Math_pages.txt")
	bot.bot.polling()

main()
