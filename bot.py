import re
import telebot
from telebot import apihelper, types

class Bot():
	def __init__(self):
		self.pages = []
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
	bot.bot.send_message(message.chat.id, 'Hello ' + message.from_user.first_name)

@bot.bot.callback_query_handler(lambda query: re.match('next page', query.data))
def handle_callback(query):
	pageNum = int(re.findall('[0-9\.]+', query.data)[0])

	if 0 <= pageNum and pageNum < len(bot.pages):
		bot.bot.send_document(query.message.chat.id, open('./Book/Math_page' + str(pageNum) + '.pdf', 'r'), reply_markup=bot.getNextPageKeyboard(pageNum+1))
	else:
		bot.bot.send_message(query.message.chat.id, "There isn't next page");

@bot.bot.message_handler(content_types=['text'])
def send_text(message):
	if re.match('^[0-9]+(\.[0-9]+)?$', message.text):
		pageNum = bot.findPageNumOfTask(float(message.text))
		if pageNum == -1:
			bot.bot.send_message(message.chat.id, "There isn't this task in book!")
			return

		bot.bot.send_document(message.chat.id, open('./Book/Math_page' + str(pageNum) + '.pdf', 'r'), reply_markup=bot.getNextPageKeyboard(pageNum+1))
	else:
		bot.bot.send_message(message.chat.id, 'You have to enter integer/float number of task')

def main():
	bot.createPages("./Book/Math_pages.txt")
	bot.bot.polling()

main()
