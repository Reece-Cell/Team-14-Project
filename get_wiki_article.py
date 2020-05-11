from urllib.request import Request, urlopen
import json
import requests
import re
#import gpt_2_simple as gpt2
import time
'''
def gen_text(samples):
	model_name = "355M"
	sess = gpt2.start_tf_sess()
	gpt2.load_gpt2(sess, model_name=model_name)
	while True:
		print("Took ", time.time() - start_time, "to get here.")
		gpt2.generate(sess,
              model_name=model_name,
              prefix="The secret to life is",
              length=500,
              temperature=0.7,
              top_p=0.9,
              top_k=40,
              return_as_list=True,
              include_prefix=False
              )
'''
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

	for i in range(len(section_names)):
		print(section_names[i])
		print()

	for banned_section in banned_sections:
		try:
			section_dict.pop(banned_section)
		except:
			pass
	return section_dict

API_URL1 = "https://en.wikipedia.org/w/api.php?action=query&format=json&prop=revisions&titles="
API_URL2 = "&formatversion=2&rvprop=content&rvslots=*"
gui_input_string = input("Enter article name: ")
gui_input_string = gui_input_string.strip().replace(" ", "_")
my_page = API_URL1+gui_input_string+API_URL2;
#try:
response = requests.get(my_page)
content = response.json()["query"]["pages"][0]["revisions"][0]["slots"]["main"]["content"]
#print(content)
parsed = parseWiki(content)
#print(parsed)
sections = section_dict(parsed)
for i in sections:
	print(i, sections[i])
'''
sentences = re.findall(r".*?[\.!?]\s?[A-Z]", parsed)
for i in range(len(sentences)):
	if i < len(sentences)-1:
		sentences[i+1] = sentences[i][-1] + sentences[i+1]
	sentences[i] = sentences[i][:-2]
	if not sentences[i][-1] == ".":
		sentences[i] = sentences[i] + "."
	#print(sentences[i])
'''
#gen_text(sentences)
#except:
#print("We can't help you with that topic, please try something else")
start_time = time.time()
#gen_text("hello")	