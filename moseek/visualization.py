## 데이터 시각화
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import math
import resource_control as rc
import mpld3

class Population:
  def __init__(self, condition, gender, healthy_condition, maxAge, minAge, enrollmentNum):
    self.condition = condition
    self.gender = gender
    self.healthy_condition = healthy_condition    
    self.maxAge = maxAge
    self.minAge = minAge
    self.enrollmentNum = enrollmentNum
class info_Trial:
  def __init__(self, official_title, title, objective, complete_time, NCTID):
    self.official_title = official_title
    self.title = title
    self.objective = objective    
    self.complete_time = complete_time
    self.NCTID = NCTID
class ArmGroup:
  def __init__(self, ArmGroupType, ArmGroupLabel, InterventionDescription):
    self.armGroupType = ArmGroupType
    self.armGroupLabel = ArmGroupLabel
    self.interventionDescription = InterventionDescription
class Intervention:
  def __init__(self, masking, allocation, washout_period, enrollment, namelist, ratio):
    self.masking = masking
    self.allocation = allocation
    self.washout_period = washout_period
    self.enrollment = enrollment
    self.namelist = namelist
    self.ratio = ratio
class Information:
  def __init__(self, designModel, population, info_trial, armGroup, intervention):
    self.designModel = designModel
    self.population = population
    self.info_trial = info_trial
    self.armGroup = armGroup
    self.intervention = intervention
# import requests

## data extraction
def get_info(url):
  infoDict = rc.request_call(url)
  
  ##designmodel##
  designModel = infoDict["DesignModel"]

  ##population##
  condition = infoDict['PopulationBox']['Condition']
  gender=infoDict['PopulationBox']['Gender']
  healthy_condition=infoDict['PopulationBox']['HealthyCondition']
  maxAge=infoDict['PopulationBox']['MaxAge']
  minAge=infoDict['PopulationBox']['MinAge']
  enrollmentNum=infoDict['PopulationBox']['Participant']
  
  population = Population(condition, gender,healthy_condition, maxAge,minAge, enrollmentNum)

  ##info_trial##
  official_title=infoDict['OfficialTitle']
  objective=infoDict['Objective']
  complete_time = infoDict['CompleteTime']
  title = infoDict['Title']
  NCTID = infoDict['NCTID']

  info_trial = info_Trial(official_title, title, objective,complete_time, NCTID)

  ##Armgroup##
  ArmGroupType = []
  ArmGroupLabel = []
  InterventionDescription = []
  #armGroupName
  info_list = infoDict['DrugInformation']['ArmGroupList']
  for i in info_list:
    ArmGroupType.append(i['ArmGroupType'])
    ArmGroupLabel.append(i['ArmGroupLabel'])
    InterventionDescription.append(i['InterventionDescription'])
    
  armGroup = ArmGroup(ArmGroupType, ArmGroupLabel, InterventionDescription)
  

  ##intervetntion##
  masking = infoDict['Masking']
  allocation = infoDict['Allocation']
  ratio = infoDict['PopulationRatio']
  # print(infoDict)
  washout_period = infoDict['WashoutPeriod']
  enrollment = infoDict['Enrollment']
  namelist = infoDict['InterventionName'].split(',')
  intervention = Intervention(masking, allocation, washout_period, enrollment, namelist, ratio)

  return Information(designModel, population, info_trial, armGroup, intervention)
# 좌표 class
class Point:
  def __init__(self, x, y):
    self.x = x
    self.y = y
def stringGoDown(ax,inString, ea, x,y,fontSize, delta):
  point = 0
  slist=[]
  while len(inString)>ea:
    point = inString[:ea].rfind(" ")
    if point==-1:
      slist.append(inString[:ea])
      inString = inString[ea:]
    else:
      slist.append(inString[:point+1])
      inString=inString[point+1:]
  slist.append(inString)
  n=len(slist)
  for i,st in enumerate(slist):
    ax.text(x, y-delta*i, st, size=fontSize)
  return n # 몇줄 짜리 문자열인지 반환
  
def stringGoUp(ax,inString, ea, x,y, fontSize, delta):
  point = 0
  slist=[]
  while len(inString)>ea:
    point = inString[:ea].rfind(" ")
    if point==-1:
      slist.append(inString[:ea])
      inString = inString[ea:]
    else:
      slist.append(inString[:point+1])
      inString=inString[point+1:]
  slist.append(inString)
  n=len(slist)
  for i,st in enumerate(slist):
    ax.text(x, y-delta*i+n*delta, st, size=fontSize)
  return n # 몇줄 짜리 문자열인지 반환

def countLine(inString, ea): # 라인 개수 반환
  point = 0
  slist=[]
  while len(inString)>ea:
    point = inString[:ea].rfind(" ")
    if point==-1:
      slist.append(inString[:ea])
      inString = inString[ea:]
    else:
      slist.append(inString[:point+1])
      inString=inString[point+1:]
  slist.append(inString)
  n=len(slist)
  return n

def bboxString(ax,x,y,inString, ea, fontSize, boolean):
  point=0
  boxString=""
  while len(inString)>ea:
    point = inString[:ea].rfind(" ")
    if point==-1:
      boxString+= (inString[:ea])+ "\n"
      inString = inString[ea:]
    else:
      boxString+= inString[:point+1] + "\n"
      inString=inString[point+1:]
  boxString+= inString
  if boolean:
    box = { 
      'ec': "black",  # ec: edgeColor, fc: faceColor
      'fc': "white"}
    ax.text(x, y,  boxString, size=fontSize, bbox=box)
  else:
    ax.text(x, y,  boxString, size=fontSize)

  
def bboxStringLine(inString, ea):
  point=0
  boxString=""
  i=0 #line 개수
  while len(inString)>ea:
    point = inString[:ea].rfind(" ")
    i+=1
    if point==-1:
      boxString+= (inString[:ea])+ "\n"
      inString = inString[ea:]
    else:
      boxString+= inString[:point+1] + "\n"
      inString=inString[point+1:]
  boxString+= inString
  i+=1
  return i

def drawPopulation(ax, startPoint, startW, box, population):
  gender = population.gender
  healthy_condition = population.healthy_condition
  maxAge = population.maxAge
  minAge = population.minAge
  
  dx = 0.1
  dy = 0.1 # 위치 조절량

  #높이 구하기
  cLine = countLine(population.condition, 48)
  # sLine = countLine(summary, 48)
  # height = (cLine + sLine +4)/10+0.1  # 임시로 4 넣기 
  height = (cLine +4)/10+0.1  # 임시로 4 넣기 

    #박스 그리기
  ax.add_patch(
    patches.Rectangle(
      (startPoint.x, startPoint.y), # bottom and left rect
        startW, #너비
        height, #높이
        edgecolor = 'blue',
        # facecolor = 'red',
        fill = False
    )
  )
  ax.text(startPoint.x+startW/2 -1, startPoint.y+height, 'Population', bbox = box)

  #populaton 박스에 정보 쓰기 
  n = stringGoDown(ax,population.condition, 48, startPoint.x+dx, startPoint.y+height-dy-0.05, 10, 0.1,) #condition
  ax.text(startPoint.x+dx, startPoint.y+height-n*dy-0.05-dy, "Gender: "+ gender) #gender
  ax.text(startPoint.x+dx, startPoint.y+height-n*dy-0.05-dy*2, "Healthy condition: "+ healthy_condition) #healthy_condition
  ax.text(startPoint.x+dx, startPoint.y+height-n*dy-0.05-dy*3, "minAge: "+ minAge) #minAge
  ax.text(startPoint.x+dx, startPoint.y+height-n*dy-0.05-dy*4, "maxAge: "+ maxAge) #maxAge
  # stringGoDown(ax, summary, 48, startPoint.x+dx, startPoint.y+height-n*dy-0.05-dy*5, 10, 0.1) #summary

  return height #줄에 맞게 조정된 높이 값

def drawInfo_Trial(ax, durationPoint, startPoint, startH, legendPoint, numArm,info_trial):
      #objective
      objPoint = Point(startPoint.x, startPoint.y+startH +0.7)
      bboxString(ax, objPoint.x, objPoint.y, "Objective: " + info_trial.objective, 140, 10, 1)
      objective_line = bboxStringLine("Objective: " + info_trial.objective, 140) # objective 줄 개수

      # info_trial.title
      titlePoint = Point(objPoint.x, objPoint.y+objective_line/10+0.1)
      bboxString(ax, titlePoint.x, titlePoint.y, "Title: "+ info_trial.title, 130, 15, 1)


      #complete_time
      period = str(info_trial.complete_time)+" months required to complete"
      ax.plot([durationPoint.x, durationPoint.x], [durationPoint.y, durationPoint.y + startH*2], color = "black", lw = "1")
      ax.text(durationPoint.x-1, durationPoint.y-0.1, period)

      # info_trial.official title
      officialPoint = Point(startPoint.x, startPoint.y-startH/2)
      bboxString(ax, officialPoint.x, legendPoint.y - (numArm+1)*startH/3, "Official Title: " +  info_trial.official_title, 140, 10, 1)

      return [legendPoint.y - (numArm+1)*startH/8 -0.5 ,titlePoint.y +0.5 ]
def drawPreIntervention(ax, numberPoint, numberW, allocationPoint, radius, intervention):
  ax.add_patch(
      patches.Arrow(
          numberPoint.x, numberPoint.y, numberW, 0, width=0.5 # 시작지점x, 시작y, x얼마나, y얼마나, 화살표두께
      )
  )
  ax.text(numberPoint.x+0.3, numberPoint.y+0.3, 'N='+str(intervention.enrollment))
  ax.text(numberPoint.x+0.3, numberPoint.y-0.3, 'M='+str(intervention.masking)) 

  # allocation
  ax.add_patch(
      patches.Circle(
          (allocationPoint.x, allocationPoint.y), radius
      )
  )
  ax.text(allocationPoint.x-0.1, allocationPoint.y, intervention.allocation[0])

  ax.text(allocationPoint.x-radius, allocationPoint.y+radius+0.1, intervention.ratio)
def writeIntervention(ax, startPoint, startH, armGLinePoint1, armGW, armGArrowW, designModel, armG, intervention):
  numBranch = len(armG.interventionDescription)
  fontArm = {'size': 9}
  #도형의 영역 내에 글자 적히게 하기
  if designModel == "Crossover Assignment":
    bfWashPoint = armGLinePoint1.x+armGW+armGArrowW/3
    afWashPoint = armGLinePoint1.x++armGArrowW/3*2
    washH = armGLinePoint1.y-startH/2-0.4
    #intervention 글자 적기
    
    for i in range(numBranch):
      drugInfo = armG.interventionDescription[i]
      drugdescription = ""
      for j in range(len(drugInfo)):
        drugdescription += drugInfo[j]["DrugName"] +"(" + drugInfo[j]["Dosage"] + ") "
      
      #꼬기 전
      stringGoUp(ax, drugdescription, 30, armGLinePoint1.x+armGW + 0.1, startPoint.y+startH-i*((startH)/(numBranch-1)), 10, 0.1)
      ax.text(armGLinePoint1.x+armGW+0.6, startPoint.y+startH-i*((startH)/(numBranch-1))-0.1, drugInfo[0]['Duration'], fontdict=fontArm)
      #꼰 후
      stringGoUp(ax, drugdescription, 30, armGLinePoint1.x + armGArrowW/3*2+0.1, startPoint.y+  i*((startH)/(numBranch-1)), 10, 0.1)
      ax.text(armGLinePoint1.x + armGArrowW/3*2+0.6, startPoint.y+i*((startH)/(numBranch-1))-0.1, drugInfo[0]["Duration"], fontdict=fontArm)
    
    bfWashPoint = armGLinePoint1.x + armGW+armGArrowW/3
    afWashPoint = armGLinePoint1.x + armGArrowW/3*2
    ##crossover 약 먹는 기간 텍스트
    ax.text((armGLinePoint1.x+bfWashPoint)/2, washH-0.1, armG.interventionDescription[0][0]['Duration'])
    ax.text((bfWashPoint+afWashPoint)/2-0.56, washH+0.05, "Washout period")
    ax.text((bfWashPoint+afWashPoint)/2-0.4, washH-0.05, intervention.washout_period)
    ax.text((afWashPoint+armGLinePoint1.x+armGW+armGArrowW)/2, washH-0.1, armG.interventionDescription[1][0]['Duration'])
    
  elif ((designModel == "Single Group Assignment" and numBranch == 1) or numBranch==1): # numBranch 추가한 이유: single 이지만 군이 여러개인 경우 때문.
    drugInfo = armG.interventionDescription[0]
    drugdescription = ""
    for i in range(len(drugInfo)):
      drugdescription += drugInfo[i]["DrugName"] +"(" + drugInfo[i]["Dosage"] + ") "
    
    textStartX = armGLinePoint1.x+armGW + 0.1
    testStartY = startPoint.y+startH/2
    stringGoUp(ax, drugdescription, 90, textStartX, testStartY, 10, 0.1)
    ax.text(textStartX+armGArrowW-0.3 , testStartY-0.2, drugInfo[0]["Duration"])
  
  else: # parallel and sequential design
    for i in range(numBranch):
      drugInfo = armG.interventionDescription[i]
      # print("군마다 사용하는 약물 리스트를 따로 만들면 좋겠다? 한번 고민. 밑에 고쳐야됨")
      try:
        textStartX = armGLinePoint1.x+armGW + 0.1
        testStartY = startPoint.y+startH-0.1
        drugdescription = ""
        for q in range(len(drugInfo)):
          drugdescription += drugInfo[q]["DrugName"]+"(" + drugInfo[q]["Dosage"] + ") "
        stringGoUp(ax, drugdescription, 40, textStartX, testStartY-i*((startH)/(numBranch-1)), 10, 0.08)
        ax.text(textStartX+armGArrowW-0.3 , testStartY-i*((startH)/(numBranch-1))-0.05, drugInfo[0]["Duration"])
      except: #no intervention인 경우만 있음
        ax.text(textStartX, testStartY-i*((startH)/(numBranch-1))+0.1, "No intervention", fontdict=fontArm)
  
def drawBranch(ax, armGLinePoint1, armGW, armGArrowW, startPoint, startH, legendPoint, intervention, designModel, armG):
  colorBranch = ['lightcoral', 'gold', 'limegreen', 'forestgreen', 'cornflowerblue', 'royalblue', 'violet', 'pink']
  armColorDict = {'Experimental': 'lightcoral', 'Active Comparator': 'gold', 'Placebo Comparator': 'limegreen', 'No Intervention': 'forestgreen', 'Other': 'cornflowerblue', 'Sham Comparator': 'royalblue', None: 'violet'}
  setArmGroup = set(armG.armGroupType) # 중복 없애기 위해 집합 함수 사용함
  ListArmGroup = list(setArmGroup) # 집합을 리스트로!
  numBranch = len(armG.interventionDescription)
  factorialColordict = {}

  #show which color follows which arm group / 범례 표현 
  if(designModel != "Factorial Assignment"):
    for i in range(len(setArmGroup)):
      ax.plot([legendPoint.x, legendPoint.x + 1], [legendPoint.y -i*startH/8, legendPoint.y -i*startH/8], armColorDict[ListArmGroup[i]])
      ax.text(legendPoint.x + 1 + 0.1 , legendPoint.y -i*startH/8, ListArmGroup[i])
  else: # factorial assignment인 경우
    for i in range(0, 2):
      deltaWidth = 3.2
      sqrtNumBranch = int(math.sqrt(numBranch))
      for j in range(0, sqrtNumBranch):
        interventionNameInDict = intervention.namelist[i*sqrtNumBranch + j]
        ax.plot([legendPoint.x + i*deltaWidth, legendPoint.x + 1 + i*deltaWidth], [legendPoint.y -i*startH/8, legendPoint.y -i*startH/8], colorBranch[j])
        ax.text(legendPoint.x + 1 + 0.1 + i*deltaWidth , legendPoint.y -i*startH/8, interventionNameInDict)
        interventionNameDict = interventionNameInDict.lower()
        factorialColordict[interventionNameDict] = colorBranch[j]

  ## design model에 따라 모양 다르게 하기
  #### 0706 수정필요###
  if(designModel=="Factorial Assignment"): # axa 인 형식만 지원. axaxa는 지원 안함. 지금으로선..
    sqrtNumBranch = int(math.sqrt(numBranch))
    branchCnt = 0
    ## 두가지 파트로 나눈다. drug/ device/ 기간 끼리.. 색을 각 분야별로 할당하기 위함.
    colorPart1 = colorBranch[0]
    colorPart2 = colorBranch[0]
    # intervention의 색과 branch 색 맞춰주기
    ## 두가지 파트로 나눈다. drug/ device/ 기간 끼리..
    interPart1 = intervention.namelist[:sqrtNumBranch]
    interPart2 = intervention.namelist[sqrtNumBranch:]
    # 길이가 긴 애들부터 색을 매치하기 위해 정렬
    interPart1.sort(key=len)
    interPart1.reverse()
    interPart2.sort(key=len)
    interPart2.reverse()
    for i in range(sqrtNumBranch):
      for j in range(sqrtNumBranch):
        # intervention끼리의 색 맞추기
        for k in range(sqrtNumBranch):
          # armGName = (armG.armGroupLabel[i*sqrtNumBranch + j]).lower()
          armGInter = (armG.interventionDescription[i*sqrtNumBranch + j]).lower()
          if(interPart1[k].lower() in armGInter):
              colorPart1 = factorialColordict[interPart1[k].lower()]
        
        for k in range(sqrtNumBranch):
          armGInter = (intervention.namelist[i + j]).lower()
          if(interPart2[k].lower() in armGInter):
              colorPart2 = factorialColordict[interPart2[k].lower()]
              break;
        ## 그림 그리기
        ax.plot([armGLinePoint1.x,armGLinePoint1.x+armGW], [armGLinePoint1.y, startPoint.y+startH-branchCnt*((startH)/(numBranch-1))], colorPart1) ## startH를 넘을 경우도 고려해야됨. 나중에 수정.
        ax.plot([armGLinePoint1.x+armGW, armGLinePoint1.x+armGW + armGArrowW/2], [startPoint.y+startH-branchCnt*((startH)/(numBranch-1)), startPoint.y+startH-branchCnt*((startH)/(numBranch-1))],colorPart1)
        ax.add_patch(
            patches.Arrow(
              armGLinePoint1.x + armGW + armGArrowW/2, startPoint.y+startH-branchCnt*((startH)/(numBranch-1)), armGArrowW/2, 0, width=0.05 # 시작지점x, 시작y, x얼마나, y얼마나, 화살표두께
              , edgecolor = colorPart2, facecolor = colorPart2
          )
        )
        branchCnt+=1

  elif(designModel == "Crossover Assignment"): # 2개 군만 있다고 가정. 
    for i in range(numBranch):
      color = armColorDict[armG.armGroupType[i]]
      ax.plot([armGLinePoint1.x,armGLinePoint1.x+armGW], [armGLinePoint1.y, startPoint.y+startH-i*((startH)/(numBranch-1))], color) ## startH를 넘을 경우도 고려해야됨. 나중에 수정.
      ax.add_patch(
          patches.Arrow(
            armGLinePoint1.x+armGW, startPoint.y+startH-i*((startH)/(numBranch-1)), armGArrowW/3, 0, width=0.05 # 시작지점x, 시작y, x얼마나, y얼마나, 화살표두께
            , edgecolor = color, facecolor = color
        )
      )
      ax.plot([armGLinePoint1.x+armGW+armGArrowW/3,armGLinePoint1.x+armGArrowW/3*2], [startPoint.y+startH-i*((startH)/(numBranch-1)), startPoint.y  + i*((startH)/(numBranch-1))], color)
      ax.add_patch(
          patches.Arrow(
            armGLinePoint1.x + armGArrowW/3*2, startPoint.y+i*((startH)/(numBranch-1)), armGArrowW/3, 0, width=0.05 # 시작지점x, 시작y, x얼마나, y얼마나, 화살표두께
            , edgecolor = color, facecolor = color
        )
      )
    
    ##crossover 약 먹는 기간 화살표
    bfWashPoint = armGLinePoint1.x+armGW+armGArrowW/3
    afWashPoint = armGLinePoint1.x++armGArrowW/3*2
    washH = armGLinePoint1.y-startH/2-0.4
    ax.plot([armGLinePoint1.x, armGLinePoint1.x+armGW + armGArrowW], [washH, washH], 'black')
    ax.plot([bfWashPoint, bfWashPoint], [washH-0.1, washH+0.1], 'pink')
    ax.plot([afWashPoint, afWashPoint], [washH-0.1, washH+0.1], 'pink')

  elif(designModel=="Parallel Assignment" or numBranch != 1): # single group이지만 군이 여러개인 경우를 포함하기 위해 numbBranch도 추가
    for i in range(numBranch):
      color = armColorDict[armG.armGroupType[i]] # color 이름
      ax.plot([armGLinePoint1.x,armGLinePoint1.x+armGW], [armGLinePoint1.y, startPoint.y+startH-i*((startH)/(numBranch-1))], color) ## startH를 넘을 경우도 고려해야됨. 나중에 수정.
      ax.add_patch(
          patches.Arrow(
            armGLinePoint1.x+armGW, startPoint.y+startH-i*((startH)/(numBranch-1)), armGArrowW, 0, width=0.05 # 시작지점x, 시작y, x얼마나, y얼마나, 화살표두께
            , edgecolor = color, facecolor = color
        )
      )
        
  elif(designModel == "Single Group Assignment" or numBranch == 1):############
    color = armColorDict[armG.armGroupType[0]]
    ax.plot([armGLinePoint1.x,armGLinePoint1.x+armGW], [armGLinePoint1.y, startPoint.y+startH/2], color) ## startH를 넘을 경우도 고려해야됨. 나중에 수정.
    ax.add_patch(
        patches.Arrow(
          armGLinePoint1.x+armGW, startPoint.y+startH/2, armGArrowW, 0, width=0.05 # 시작지점x, 시작y, x얼마나, y얼마나, 화살표두께
          , edgecolor = color, facecolor = color
      )
    )
def visualization(info):
  ##initialize
  designModel = info.designModel
  population = info.population
  info_trial = info.info_trial
  armGroup = info.armGroup
  intervention = info.intervention

  plt.style.use('default') #스타일 설정: https://hong-yp-ml-records.tistory.com/88
  plt.rcParams['figure.figsize'] = (9, 8) # 차트의 기본 크기 설정
  plt.rcParams['font.size'] = 10 # fontsize


  fig, ax = plt.subplots()
  ax.plot() # 0번: x값, #1번: y값

  #box1 style
  box1 = {'boxstyle': 'round', 
          'ec': (1.0, 0.5, 0.5), # ec: edgeColor, fc: faceColor
          'fc': (1.0, 0.8, 0.8)}

  #population
  startPoint = Point(10, 10) 
  startW = 4
  startH = drawPopulation(ax, startPoint, startW, box1, population)
  ###################

  # Number, Masking
  numberPoint = Point(startPoint.x+startW, startPoint.y + startH/2) 
  numberW = 2
  # allocation
  radius = 0.2
  allocationPoint = Point(numberPoint.x+numberW+radius, numberPoint.y) 
  # ###################
  drawPreIntervention(ax, numberPoint, numberW, allocationPoint, radius, intervention)

  #branch
  armGLinePoint1 = Point(allocationPoint.x + radius, allocationPoint.y) 
  armGW = 1
  armGArrowW = 7
  legendPoint = Point(startPoint.x,startPoint.y-startH/6)
  ###################
  drawBranch(ax, armGLinePoint1, armGW, armGArrowW, startPoint, startH, legendPoint, intervention, designModel, armGroup)
  writeIntervention(ax, startPoint, startH, armGLinePoint1, armGW, armGArrowW, designModel, armGroup, intervention)

  ###info_trial
  durationPoint = Point(armGLinePoint1.x+armGW+armGArrowW+1, allocationPoint.y-startH)
  numArm = len(armGroup.armGroupLabel)
  ylim=drawInfo_Trial(ax, durationPoint, startPoint, startH, legendPoint, numArm,info_trial)

  ax.set_xlim(8.0, 26.0)
  ax.set_ylim(ylim[0], ylim[1])
  ax.set_xticks([])
  ax.set_yticks([])
  # ax.axis("off")
  chartpage(fig)

  # Html_str = mpld3.fig_to_html(fig)
  # Html_file= open("./myapp/templates/index.html","at")
  # Html_file.write(Html_str)
  # Html_file.close()
  
  return info_trial.NCTID

def chartpage(fig):

  startInherit = "{% extends 'chartbase.html' %} \n {% load static %} \n {% block content %}\n"
  styleLink = '<link rel="stylesheet" type="text/css" href="{% static \'css/detail.css\' %}">\n'
  # dtemplate2 = "{% endblock %}"
  styleStart='<div id="container">\n'
  graphTag1 = '<div id="graph">\n'
  graphTag2 = '</div>\n'
  Html_str = mpld3.fig_to_html(fig)
  Html_file= open("./chart/templates/chart.html","w")
  Html_file.write(startInherit + styleLink + styleStart + graphTag1 + Html_str + graphTag2)
  Html_file.close()

def giveMeURL(url):
  case = get_info(url)
  return visualization(case)
