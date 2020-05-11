# Author: Eric Orozco Viscarra
# Date: 3/9/2020
# Course: CST205: Multimedia Programming
# Abstract: This program ...

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QLineEdit, QComboBox
from PyQt5.QtGui import QColor, QPixmap, QIcon
from PyQt5.QtCore import pyqtSlot
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
	content = re.sub(r"=*\s*See also.*", "", content)
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

def gen_text(samples):
	start_time = time.time()
	model_name = "355M"
	sess = gpt2.start_tf_sess()
	gpt2.load_gpt2(sess, model_name=model_name)
	print("Took ", time.time() - start_time, "to load the model here.")
	for i in range(4):
		print(gpt2.generate(sess,
              model_name=model_name,
              prefix="The secret to life is",
              length=300,
              temperature=0.7,
              top_p=0.9,
              top_k=40,
              return_as_list=True,
              include_prefix=False
              ))
		print("Took ", time.time() - start_time, "to generate text.")

class MainWindow(QWidget):
	def __init__(self):
		super().__init__()
		self.vbox = QVBoxLayout()

		self.setWindowTitle("Eassay")

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
		my_page = API_URL1+topic+API_URL2;
		try:
			response = requests.get(my_page)
			content = response.json()["query"]["pages"][0]["revisions"][0]["slots"]["main"]["content"]
			parsed = parseWiki(content)
			if self.state == "Topic and Error":
				self.vbox.removeWidget(self.invalid_topic_expl)
				self.invalid_topic_expl.deleteLater()
				self.invalid_topic_expl = None
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
				self.focuses.addItem(section)
			self.make_essay_btn = QPushButton("Make My Essay")
			self.make_essay_btn.clicked.connect(self.make_essay)
			self.vbox.addWidget(self.focus_expl)
			self.vbox.addWidget(self.focuses)
			self.vbox.addWidget(self.make_essay_btn)
			self.setLayout(self.vbox)
			self.state = "Focus"
		except:
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
	def make_essay(self):

		intro = sentencify(self.sections["Introduction"])

		focus = sentencify(self.sections[self.focuses.currentText()])

		gen_text(intro)

		gen_text(focus)


app = QApplication(sys.argv)
main_win = MainWindow()
main_win.show()

sys.exit(app.exec_())