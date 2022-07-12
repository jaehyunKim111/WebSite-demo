from urllib.request import urlopen
from attr import attr
from bs4 import BeautifulSoup
import requests

def originalText(nctID):
  url = "https://www.clinicaltrials.gov/ct2/show/" + nctID
  res = requests.get(url)
  soup = BeautifulSoup(res.text, "lxml")
  box = str(soup.find('div', attrs={"id": "main-content"}))

  # tag들
  link='''<link rel="stylesheet" href="../static/css/trial-record.css">\n
<link rel="stylesheet" href="../static/css/w3-ct.css">\n
<link rel="stylesheet" href="../static/css/print.css">\n'''
  styleEnd='</div>\n'
  trialTag1 = '<div id="trial">\n'
  trialTag2 = '</div>\n'
  endinhert = "{% endblock %}"
  ####

  Html_file= open("./chart/templates/chart.html","a", encoding='UTF-8')
  Html_file.write(link + trialTag1 + box+ trialTag2 + styleEnd + endinhert)
  Html_file.close()