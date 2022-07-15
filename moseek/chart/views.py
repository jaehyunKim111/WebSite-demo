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
    # model = request.POST['ex_url']    # request.POST: 입력 받은 값  POST['name']: name값으로 받음
    # print("\n\n"+model+"\n\n")
    url = "https://clinicaltrials.gov/ct2/show/"
    number = request.POST['NCT'] #submit이 아니어서 안 먹는 듯
    number = int(number)
    nctList=["NCT05446467", "NCT03727152", "NCT03457311", "NCT02040376", "NCT04450953", "NCT03208218", "NCT00482833", "NCT03507790", "NCT01723228",]
    url += nctList[number]
    NCTID = visualization.giveMeURL(url)
    crawling.originalText(NCTID)
    return render(request, 'chart.html')