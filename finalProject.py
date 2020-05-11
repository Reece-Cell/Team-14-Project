# Author: Eric Orozco Viscarra
# Date: 3/9/2020
# Course: CST205: Multimedia Programming
# Abstract: This program ...

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from urllib.request import Request, urlopen
import json
import requests
import re
import gpt_2_simple as gpt2
import time

def parseWiki(content):
	while content != re.sub(r"{{[^{]*?}}", "", content):
		# Continue to delete nests
		content = re.sub(r"{{[^{]*?}}", "", content)
	# Remove lines with "*" (lists probably)
	content = re.sub(r"\*.*", "", content)
	# Remove subsection headers that have n-=
	content = re.sub(r"={3,}.*=+", "", content)
	# Remove side box sections that show pictures
	content = re.sub(r"\[\[File:.*]]", "", content)
	# Get rid of end of lines so end string will be one long line, easily split
	content = content.replace("\n", "")
	# Dealing with nested {{ }}
	# As long as we are still deleting nests
	while content != re.sub(r"{{[^{]*?}}", "", content):
		# Continue to delete nests
		content = re.sub(r"{{[^{]*?}}", "", content)
	content = re.sub(r"\{\|.*?\|\}", "", content)
	content = re.sub(r"'''", "", content)
	content = re.sub(r"<!--.*?-->", "", content)
	content = re.sub(r"<[^/]*?/>", "", content)
	content = re.sub(r"<.*?>.*?</.*?>", "", content)
	content = re.sub(r"\[\[[^\]\]]*\|", "", content)
	content = re.sub(r"\[\[", "", content)
	content = re.sub(r"]]", "", content)
	content = re.sub(r"''", "", content)
	content = re.sub(r"&nbsp;", " ", content)
	content = re.sub(r"\s?\(.*?\)", "", content)
	content = re.sub(r"}}", "", content)
	content = re.sub(r"\s{2,}", " ", content)
	content = re.sub(r"\\", "", content)
	content = re.sub(r"=*\s*See also.*", "", content)
	return content

def parse_gpt(content):
	content = re.sub(r"(\\n)+", " ", content)
	content = re.sub(r"<\|endoftext\|>", " ", content)
	content = re.sub(r"\s{2,}", " ", content)
	content = re.sub(r"\\", "", content)
	return content

def section_dict(parsed_article):
	banned_sections = ["See also", "References", "Notes", "Further reading", "External links", "Citations", "Honors and awards"]
	section_names = re.findall(r"={2,}.*?=+", parsed_article)
	section_names.insert(0, "Introduction")

	for i in range(len(section_names)):
		section_names[i] = section_names[i].replace('=', '')
		section_names[i] = section_names[i].strip()

	section_content = re.split(r"={2,}.*?=+", parsed_article)
	section_dict = {section_names[i]: section_content[i] for i in range(len(section_names))} 

	for banned_section in banned_sections:
		try:
			section_dict.pop(banned_section)
		except:
			pass
	return section_dict

def sentencify(str):
	sentences = re.findall(r".*?[\.!?]\s?[A-Z]", str)
	for i in range(len(sentences)):
		if i < len(sentences)-1:
			sentences[i+1] = sentences[i][-1] + sentences[i+1]
		sentences[i] = sentences[i][:-2]
		if not sentences[i][-1] == ".":
			sentences[i] = sentences[i] + "."
		sentences[i] = sentences[i].strip()
	return sentences

def combine_sentences(sentences):
	full_text = ""
	for sentence in sentences:
		full_text = full_text + sentence + " "
	full_text = full_text.strip()
	return full_text

def gen_text(sample):
	#model_name = "355M"
	#sess = gpt2.start_tf_sess()
	#gpt2.load_gpt2(sess, model_name=model_name)
	return gpt2.generate(sess,
          model_name=model_name,
          prefix=sample,
          length=300,
          temperature=0.7,
          top_p=0.9,
          top_k=40,
          return_as_list=True,
          include_prefix=False
          )

class MainWindow(QWidget):
	def __init__(self):
		super().__init__()
		self.vbox = QVBoxLayout()

		self.setWindowTitle("Essay Generator")

		self.state = "Only Topic"

		self.topic_expl = QLabel("Main Topic of Paper:")

		self.paper_topic = QLineEdit()

		self.topic_btn = QPushButton("Get Focuses")
		self.topic_btn.clicked.connect(self.get_focuses)

		self.vbox.addWidget(self.topic_expl)
		self.vbox.addWidget(self.paper_topic)
		self.vbox.addWidget(self.topic_btn)

		self.setLayout(self.vbox)

	@pyqtSlot()
	def get_focuses(self):
		API_URL1 = "https://en.wikipedia.org/w/api.php?action=query&format=json&prop=revisions&titles="
		API_URL2 = "&formatversion=2&rvprop=content&rvslots=*"
		topic = self.paper_topic.text()
		topic = topic.strip().replace(" ", "_")
		my_page = API_URL1+topic+API_URL2
		try:
			response = requests.get(my_page)
			content = response.json()["query"]["pages"][0]["revisions"][0]["slots"]["main"]["content"]
			parsed = parseWiki(content)
			if self.state == "Topic and Error":
				self.vbox.removeWidget(self.invalid_topic_expl)
				self.invalid_topic_expl.deleteLater()
				self.invalid_topic_expl = None
			if self.state == "Generated":
				self.vbox.removeWidget(self.essay_done)
				self.essay_done.deleteLater()
				self.essay_done = None
				self.adjustSize()
				self.state = "Focus"
			if self.state == "Focus":
				self.vbox.removeWidget(self.focus_expl)
				self.focus_expl.deleteLater()
				self.focus_expl = None
				self.vbox.removeWidget(self.focuses)
				self.focuses.deleteLater()
				self.focuses = None
				self.vbox.removeWidget(self.make_essay_btn)
				self.make_essay_btn.deleteLater()
				self.make_essay_btn = None
			self.sections = section_dict(parsed)
			self.focus_expl = QLabel("Focus Point of Paper:")
			self.focuses = QComboBox()
			for section in self.sections:
				if not section == "Introduction":
					self.focuses.addItem(section)
			self.focuses.currentTextChanged.connect(self.clear_generate_label)
			self.make_essay_btn = QPushButton("Make My Essay")
			self.make_essay_btn.clicked.connect(self.make_essay)
			self.vbox.addWidget(self.focus_expl)
			self.vbox.addWidget(self.focuses)
			self.vbox.addWidget(self.make_essay_btn)
			self.setLayout(self.vbox)
			self.state = "Focus"
		except:
			if self.state == "Generated":
				self.vbox.removeWidget(self.essay_done)
				self.essay_done.deleteLater()
				self.essay_done = None
				self.adjustSize()
				self.state = "Focus"
			if self.state == "Focus":
				self.vbox.removeWidget(self.focus_expl)
				self.focus_expl.deleteLater()
				self.focus_expl = None
				self.vbox.removeWidget(self.focuses)
				self.focuses.deleteLater()
				self.focuses = None
				self.vbox.removeWidget(self.make_essay_btn)
				self.make_essay_btn.deleteLater()
				self.make_essay_btn = None
				self.state = "Only Topic"
			if self.state == "Only Topic":
				self.invalid_topic_expl = QLabel("Couldn't find topic, please try another!")
				self.vbox.addWidget(self.invalid_topic_expl)
				self.setLayout(self.vbox)
				self.adjustSize()
				self.state = "Topic and Error"

	@pyqtSlot()
	def clear_generate_label(self):
		if self.state == "Generated":
			self.vbox.removeWidget(self.essay_done)
			self.essay_done.deleteLater()
			self.essay_done = None
			self.adjustSize()
			self.state = "Focus"

	@pyqtSlot()
	def make_essay(self):
		essay = "[Enter Name Here]\n"
		essay += "[Enter Date Here]\n"
		essay += "[Enter Class Name Here]\n\n"
		essay += "\t\t\t\t\t[Enter Title Here]\n\t"

		intro = sentencify(self.sections["Introduction"])
		intro_sample = combine_sentences(intro[:3])
		start_time = time.time()
		intro_gen = gen_text(intro_sample)[0]
		print("Took ", time.time() - start_time, "to generate intro.")
		parsed_intro = parse_gpt(intro_gen)
		intro_sentences = sentencify(parsed_intro)
		intro_full = combine_sentences(intro_sentences)
		
		essay += intro_full

		focus = sentencify(self.sections[self.focuses.currentText()])

		sentences_per_sample = len(focus)//3

		for i in range(3):
			if len(focus) > 10:
				body_sample = combine_sentences(focus[3*i:3*(i+1)])
			elif len(focus) < 3:
				body_sample = combine_sentences(focus[:3])
			else:
				body_sample = combine_sentences(focus[0+sentences_per_sample*i:sentences_per_sample*(i+1)])
			start_time = time.time()
			body_gen = gen_text(body_sample)[0]
			print("Took ", time.time() - start_time, "to generate body paragraph " + str(i+1) + ".")
			parsed_body = parse_gpt(body_gen)
			body_sentences = sentencify(parsed_body)
			body_full = combine_sentences(body_sentences)
			essay += "\n\t"
			essay += body_full

		f = open("my_essay.txt", "w")
		f.write(essay)
		f.close()

		self.essay_done = QLabel("Your essay has been generated!")
		self.essay_done.setAlignment(Qt.AlignCenter)
		self.vbox.addWidget(self.essay_done)
		self.setLayout(self.vbox)
		self.state = "Generated"

model_name = "355M"
sess = gpt2.start_tf_sess()
gpt2.load_gpt2(sess, model_name=model_name)
app = QApplication(sys.argv)
main_win = MainWindow()
main_win.show()
sys.exit(app.exec_())