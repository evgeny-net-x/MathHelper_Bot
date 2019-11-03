import sys
import re
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import portrait
from PyPDF2 import PdfFileWriter, PdfFileReader

'''
	sed -E -e 's:<b|</page:\'$'\n&:g' |
	sed -E -n '/(<b[^>]*>[0-9]*\.)|(<page[^>]*>)/p' |
	sed -E 's:(<b[^>]*>)([0-9\.]*)(.*):\2:g' |
	sed -E 's:\.$::g' |
	sed -E 's:<page id="([0-9]*)"(.*):page \1:g' |
	sed -e ':a' -e 'N' -e '$!ba' -e 's/\n/ /g' |
	sed -E 's: page:\'$'\npage:g' |
	sed -E 's:[\.]\+::g' |
	sed -E 's: \.*: :g' |
	tr -s ' ' ' ' |
	sed -E 's:[\.]\+::g' |
	sed -E 's:(page [0-9\.]* [0-9\.]*)(.*)([0-9] ([0-9\.]*)$):\1-\4:g'
'''

class PDF_Parser:
	def __init__(self, path_of_pdf, path_of_table):
		self.pages = []
		self.reader = PdfFileReader(open(path_of_pdf, "rb"))

		fd = open(path_of_table, "r")
		for line in fd:
			nums = re.findall("[0-9\.]+", line)
			page = int(nums[0])
			begin= float(nums[1])
			end  = begin

			if len(nums) > 2:
				end = float(nums[2])

			self.pages.append([page, begin, end])
		fd.close()

	def CreatePage(self, page_num, path_of_out):
		if not(1 <= page_num and page_num < self.reader.getNumPages()):
			return 1

		writer = PdfFileWriter()
		writer.addPage(self.reader.getPage(page_num))
		outfp = open(path_of_out, 'wb')
		writer.write(outfp)
		return 0

	def CreatePageOfTask(self, task_num, path_of_out):
		begin = 0
		end = len(self.pages)
		mid = end/2

		if not(0 <= task_num and task_num <= self.pages[end-1][2]):
			return 1

		while 1:
			if task_num < self.pages[mid][1]:
				end = mid-1
				mid = (begin+end)/2
			elif self.pages[mid][2] < task_num:
				begin = mid+1
				mid = (begin+end)/2
			else:
				break
		
		writer = PdfFileWriter()
		writer.addPage(self.reader.getPage(self.pages[mid][0]))
		outfp = open(path_of_out,'wb')
		writer.write(outfp)
		return 0
