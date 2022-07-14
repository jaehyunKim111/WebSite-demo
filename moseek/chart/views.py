from django.shortcuts import render
import visualization
import crawling
import random

def home(request):
  # if request.method =='GET':
    return render(request,'home.html')
    # return HttpResponse("""
        # <form action="/" method="post">
        # <label>
        #   URL: <input type="text" name="url" placeholder="url">
        #   <input type="submit" value="Search">
        # </label>
        # </form>
    # """)
  # elif request.method =='POST':
    # url = request.POST['url']    # request.POST: 입력 받은 값  
    # visualization.giveMeURL(url)
    # return render(request, 'home.html')    

def create(request):
  if(request.method == 'POST'):
    url = request.POST['url']    # request.POST: 입력 받은 값  POST['name']: name값으로 받음
    NCTID = visualization.giveMeURL(url)
    crawling.originalText(NCTID)
    return render(request, 'chart.html')

def example(request):
  if(request.method == 'POST'):
    model = request.POST['ex_url']    # request.POST: 입력 받은 값  POST['name']: name값으로 받음
    rand = random.randint(1,3)
    url=''
    print("\n\n"+model+"\n\n")
    if model == "crossover":
      if rand == 1:
        url = "https://clinicaltrials.gov/ct2/show/NCT02040376"
      elif rand ==2:
        url = "https://clinicaltrials.gov/api/query/full_studies?expr=The%20Effect%20of%20Eplerenone%20on%20the%20Evolution&fmt=JSON"
      else:
        url = "https://www.clinicaltrials.gov/ct2/show/NCT03208218"
    elif model == "parallel":
      if rand == 1:
        url = "https://clinicaltrials.gov/ct2/show/NCT00482833"
      elif rand ==2:
        url = "https://clinicaltrials.gov/api/query/full_studies?expr=NCT03507790&min_rnk=1&max_rnk=100&fmt=json"
      else:
        url = "https://clinicaltrials.gov/ct2/show/NCT01723228"
    else :
      if rand == 1:
        url = "https://clinicaltrials.gov/ct2/show/NCT05446467?term=pembrolizumab+in+combination+with+low-dose+pfas&draw=2&rank=1"
      elif rand ==2:
        url = "https://clinicaltrials.gov/ct2/show/NCT03727152"
      else:
        url = "https://clinicaltrials.gov/ct2/show/NCT03457311"     
    NCTID = visualization.giveMeURL(url)
    crawling.originalText(NCTID)
    return render(request, 'chart.html')