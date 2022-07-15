from urllib.request import urlopen
from bs4 import BeautifulSoup
import requests

def originalText(nctID):
  url = "https://www.clinicaltrials.gov/ct2/show/" + nctID
  res = requests.get(url)
  soup = BeautifulSoup(res.text, "lxml")

  box = soup.find('div', attrs={"id": "main-content"})
  link='''<link rel="stylesheet" href="../static/css/trial-record.css">\n
<link rel="stylesheet" href="../static/css/w3-ct.css">\n
<link rel="stylesheet" href="../static/css/print.css">\n'''
  elementTag1 = '<div id="element">\n'
  trialTag = '<div id="trial">\n'
  endTag = '</div>\n'
  scriptTag = "<script src=\"{% static 'js/resize.js' %}\"></script>"
  endinhert = "{% endblock %}"
  Html_file= open("./chart/templates/chart.html","a", encoding='UTF-8')
  Html_file.write(link + elementTag1 + trialTag + str(box)+ endTag + endTag + endTag + scriptTag + endinhert)
  Html_file.close()
