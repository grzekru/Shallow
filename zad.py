# -*- coding: utf-8 -*-

# https://github.com/grzekru/Shallow

import subprocess
import codecs
import re
import io
import sys
import fileinput

f = codecs.open('imiona.txt','r','utf-8')
imiona = f.readlines()
f.close()

f = codecs.open('nazwiska.txt','r','utf-8')
nazwiska = f.readlines()
f.close()

for i in range(len(imiona)):
	imiona[i] = imiona[i].strip()

for i in range(len(nazwiska)):
	nazwiska[i] = re.search("\\d* (\\w*)",nazwiska[i]).group(1)

input_stream = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')

for line in input_stream:
	text = line

	file = codecs.open('text.txt', 'w', 'utf-8')
	file.write(text)
	file.close()

	p = subprocess.Popen(["spejd","-c","config.ini","text.txt"],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	p.communicate()

	wynik = codecs.open('textSh.xml','r','utf-8').read()

	pattern = "<syntok.*?>.*?</syntok>"
	regex = re.compile(pattern, flags=re.MULTILINE|re.DOTALL)

	rules = list()

	for match in regex.finditer(wynik):
	    rules.append(match.group())

	zasady = list()
	orth = list()
	start = list()
	ends = list()

	for rule in rules:
		m = re.search("rule=\"(.*)\"",rule)
		zasady.append(m.group(1))
		m = re.search("<orth>(.*?)</orth>",rule)
		orth.append(m.group(1))
		m = re.search("string-range=\"string-range\\(p-1,(\\d*?),\\d*\\)\"",rule)
		start.append(m.group(1))
		m1 = re.findall("string-range=\"string-range\\(p-1,(\\d*?),\\d*\\)\"",rule)
		m2 = re.findall("string-range=\"string-range\\(p-1,\\d*,(\\d*?)\\)\"",rule)
		ends.append(int(m1[-1])+int(m2[-1]))

	def isImie(text):
		if (text in imiona):
			return True
		else:
			if (text.endswith("em")):
				return isImie(text[0:-2])
			elif (text.endswith("a")):
				return isImie(text[0:-1])
			elif (text.endswith("ego")):
				return isImie(text[0:-3])
			else:
				return False

	def isNazwisko(text):
		if (text in nazwiska):
			return True
		else:
			if (text.endswith("em")):
				return isNazwisko(text[0:-2])
			elif (text.endswith("a")):
				return isNazwisko(text[0:-1])
			elif (text.endswith("ego")):
				return isNazwisko(text[0:-3])
			else:
				return False

	def check(text,i):
		if (isImie(text) == True):
			zasady[i] = "IMIE"
		elif (isNazwisko(text) == True):
			zasady[i] = "NAZWISKO"

	zStart = None
	zStop = None
	OK = 0

	startA = list()
	stopA = list()

	def wywalKropki():
		flag = False
		for i in range(len(zasady)):
			if (flag==True and zasady[i]=="K"):
				del zasady[i]
				del orth[i]
				del start[i]
				del ends[i]
				return True
			elif (flag==True and zasady[i]!="K"):
				flag = False

			if (zasady[i] in ["ENTK","IMIE"]):
				flag = True

		return False

	while (wywalKropki()==True):
		pass

	for i in range(len(zasady)):
		if (zasady[i] == "DUZA"):
			check(orth[i],i)

		if (i==0 and zasady[i] == "DUZA"):
			if (orth[i] not in ["Profesor","Prezes","Prezydent","Dr","Dr.","Doktor","Magister"]):
				zasady[i] = "Z"
		#print(zasady[i])

		if (zasady[i] not in ["Z","K"]):
			if (zStart is None):
				zStart = start[i]
			zStop = ends[i]
			if (zasady[i] in ["IMIE","NAZWISKO"]):
				OK = OK + 1
		else:
			if (OK>0):
				startA.append(zStart)
				stopA.append(zStop)
			zStart = None
			zStop = None
			OK = 0

	if (OK>0):
		startA.append(zStart)
		stopA.append(zStop)
	zStart = None
	zStop = None
	OK = -1

	for j in range(len(startA)):
		i = len(startA)-1-j
		text = text[:int(stopA[i])] + '>' + text[int(stopA[i]):]
		text = text[:int(startA[i])] + '<' + text[int(startA[i]):]

	if (text.endswith('\n')):
		text = text[:-1]
	print(text)