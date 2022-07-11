from django.shortcuts import render
import visualization
import crawling

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
    url = request.POST['ex_url']    # request.POST: 입력 받은 값  POST['name']: name값으로 받음
    NCTID = visualization.giveMeURL(url)
    crawling.originalText(NCTID)
    return render(request, 'chart.html')