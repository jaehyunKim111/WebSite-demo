import datetime
import requests
import re
import boto3
import json
import math
import sys
#multithreading part, no need for extra pip install
from threading import Thread
from queue import Queue

###############################################
################## IMPORTANT ##################
###############################################
# MOVE ALL THE WAY DOWN TO CHECK HOW TO CALLL #
###############################################

############### Versions 1.4.2 ################
# fixed get_title, json changes depending on search by name or by NCT ID
############### Versions 1.4.1 ################
# changed washout to UppaerCamel
############### Versions 1.4.0 ################
# changed short_design -> title
# changed population_box, removed summary
# removed thread for title(short_design)
# updated washout
# added NCT ID
############### Versions 1.3.3 ################
# fixed error case in population box about key name
############### Versions 1.3.2 ################
# fixed error case in drug time_descri code
# fixed error case in washout code
############### Versions 1.3.1 ################
# fixed error case in population ratio code
# fixed error case in population box code
############### Versions 1.3.0 ################
# changed calling process of boto to allow upload without causing error in calling boto client
# erased word2num library
# updated drug_time_descri.py with precision
# change_to_url code is inserted
# updated dictionary key to UpperCamelCase
############### Versions 1.2.1 ################
# fixed wash_out typo and erase time
# optimized intervention_name
# fixed resource_control request response -> url
# fixed intevention name
############### Versions 1.2.0 ################
# previous 1.1.5 -> 1.2.0
# add multithreading to speed up
# optimized short_design
# optimized calc_date
############### Versions 1.1.4 ################
# fixed error caused in get_population_ratio()
############### Versions 1.1.3 ################
# function request - > request_call
# request_call now returns dictionary
# update in washout
############### Versions 1.1.2 ################
# function request(response) to get result
############### Versions 1.1.1 ################
# optimized population_box


#################################################################################################################################################
#################################################################################################################################################
#################################################################################################################################################
import os, json
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent

secret_file = os.path.join(BASE_DIR, 'secrets.json') # secrets.json 파일 위치를 명시

with open(secret_file) as f:
    secrets = json.loads(f.read())

def get_secret(setting, secrets=secrets):
    """비밀 변수를 가져오거나 명시적 예외를 반환한다."""
    try:
        return secrets[setting]
    except KeyError:
        error_msg = "Set the {} environment variable".format(setting)
        raise ImproperlyConfigured(error_msg)

accessKey = get_secret("aws_access_key_id")
accessSecretKey = get_secret("aws_secret_access_key")
region = get_secret("region_name")
# from decouple import config
# accessKey = config('aws_access_key_id')
# accessSecretKey = config('aws_secret_access_key')
# region = config('region_name')


comprehend = boto3.client('comprehend', aws_access_key_id=accessKey, aws_secret_access_key=accessSecretKey, region_name= region)
comprehend_med = boto3.client('comprehendmedical', aws_access_key_id=accessKey,aws_secret_access_key=accessSecretKey, region_name= region)


#################################################################################################################################################
#################################################################################################################################################
#################################################################################################################################################
def removearticles(text):
    articles = {'A': '','a': '', 'An': '','an':'', 'and':'', 'The': '','the':''}
    rest = [word for word in text.split() if word not in articles]
    return ' '.join(rest)

def get_title(response):
    title = response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['IdentificationModule']['BriefTitle']

    change_dictionary = "{%s : %s%s%s}" % ('"Title"', '"', title, '"')
    #json_acchange_dictionaryceptable_string = .replace("'", "\"")
    #d = json.loads(json_acceptable_string)
    result_dictionary = json.loads(change_dictionary)
    #print(type(result_dictionary))
    return result_dictionary


#################################################################################################################################################
#################################################################################################################################################
#################################################################################################################################################
def get_population_box(response):   

    information = {
        "Condition" : "",
        "Participant" : 0,
        "MinAge" : 0,
        "MaxAge" : "",
        "Gender" : "",
        "HealthyCondition" : "",
    }

    information["Participant"] = response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['DesignModule']['EnrollmentInfo']['EnrollmentCount']
    information['Gender'], information['HealthyCondition']  = response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']["EligibilityModule"]["Gender"], response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']["EligibilityModule"]["HealthyVolunteers"]

    try:
        information['MinAge'] = response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']["EligibilityModule"]["MinimumAge"]
    except:
        information['MinAge'] = ''
    try:
        information['MaxAge'] = response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']["EligibilityModule"]["MaximumAge"]
    except:
        information['MaxAge'] = ''

    convertString = ''.join([str(item) for item in response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['ConditionsModule']['ConditionList']['Condition']])
    information['Condition'] = convertString
    
    dic_information = {'PopulationBox' : information}
    return dic_information

#################################################################################################################################################
#################################################################################################################################################
#################################################################################################################################################
def get_calc_date(response):

    #get the api resourse
    start_time_api, end_time_api = response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['StatusModule']['StartDateStruct']['StartDate'], response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['StatusModule']['CompletionDateStruct']['CompletionDate']

    #since the text is two 'April 2020" split into two difference
    start_date, end_date = start_time_api.split(), end_time_api.split()

    #change the month->the integer num
    datetime_object, datetime_object = datetime.datetime.strptime(start_date[0], "%B"), datetime.datetime.strptime(end_date[0], "%B")
    start_month, end_month = datetime_object.month, datetime_object.month

    for value, item in enumerate(start_date):
        if len(item) > 3:
            convert_start_date = item

    for value, item in enumerate(end_date):
        if len(item) > 3:
            convert_end_date = item

    #calc the time
    require_time = (int(convert_end_date) - int(convert_start_date))*12 + (end_month-start_month)
    #print out the total month
    #print(str(require_time) + " months required to complete")
    return_dictionary = {"CompleteTime" : require_time}
    return return_dictionary


#################################################################################################################################################
#################################################################################################################################################
#################################################################################################################################################
def get_drug_time(response):

    detail_description = ""
    brief_description = ""
    drug_list = response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['ArmsInterventionsModule']['InterventionList']['Intervention']
    arm_name = response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['ArmsInterventionsModule']['ArmGroupList']['ArmGroup']

    try:
        detail_description = response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['DescriptionModule']["BriefSummary"]
    except KeyError:
        pass
    try:
        brief_description = response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['DescriptionModule']["DetailedDescription"]
    except KeyError:
        pass

    drug = []
    time_label = [' day',' days',' week',' weeks',' month',' year']
    time_label2 = ['day','week','month','year']
    amount = ['mg','g ', 'mcg', 'dose']
    drug_date = []
    dosage_que = Queue()
    
    left = 0
    right = 0
    d_left = 0
    d_right = 0

    drug_dict = {}

    Arm_group = {}
    InterventionDrug = {'ArmGroupList' : []}


    for arms in arm_name:
        try:
            Arm_group[arms['ArmGroupLabel']] = {'ArmGroupLabel' : '','ArmGroupType' : '', 'ArmGroupDescription' : '', 'InterventionList' : '', 'InterventionDescription' : []}
            Arm_group[arms['ArmGroupLabel']]['ArmGroupLabel'] = arms['ArmGroupLabel']
            Arm_group[arms['ArmGroupLabel']]['ArmGroupType'] = arms['ArmGroupType']
            Arm_group[arms['ArmGroupLabel']]['InterventionList'] = arms['ArmGroupInterventionList']
        except KeyError:
            pass

    #print(Arm_group)

    for i in range(len(drug_list)):
        drug.append(drug_list[i]['InterventionName'])
        drug_dict[drug_list[i]['InterventionName'].lower()] = {'DrugName' : '','Duration' : '', 'Dosage' : '', 'HowToTake' : ''}

    slpit = detail_description.replace(",", "").split(". ") + brief_description.replace(",", "").split(".")
 ########################################################################################
 # 밑에 코드는 description부분에 약물 복용 주기, 약물 복용량을 찾아서 넣는 코드를 작성함#
 #########################################################################################    
    for i1 in range(len(slpit)):     #시간 관련된 내용
        temp = slpit[i1].split()
        for i2 in range(len(drug)):
            if drug[i2]+ ' ' in slpit[i1]:
                drug_index = temp.index(drug[i2].split()[0])
                for i5 in range(len(time_label)):
                    for i3 in range(drug_index-1, -1, -1):
                        if time_label[i5] == temp[i3]:
                            left = i3
                            break
                    for i4 in range(drug_index, len(temp)):
                        if time_label[i5] == temp[i4]:
                            right = i4
                            break

                for i5 in range(len(amount)):
                    for i3 in range(drug_index-1, -1, -1):
                        if amount[i5] in temp[i3]:
                            d_left = i3
                            break
                    for i4 in range(drug_index, len(temp)):
                        if amount[i5] in temp[i4]:
                            d_right = i4
                            break

                if left != 0 or right != 0:
                    if left == 0 or abs(drug_index - left) >= abs(drug_index - right):
                        drug_date.append(temp[drug_index : right + 1])
                        drug_dict[temp[drug_index].lower()]['Duration'] = temp[right - 1] + " " + temp[right]
                    elif right == 0 or abs(drug_index - left) < abs(drug_index - right):
                        drug_date.append(temp[left-1 :drug_index  + 1])
                        drug_dict[temp[drug_index].lower()]['Duration'] = temp[left - 1] + " " + temp[left]
                if d_left != 0 or d_right != 0:
                    if d_left == 0 or abs(drug_index - d_left) >= abs(drug_index - d_right):
                        drug_date.append(temp[drug_index : d_right + 1]) # 복용량 관련 내용
                        drug_dict[temp[drug_index].lower()]['Dosage'] = temp[d_right - 1] + "  " + temp[d_right]
                    elif d_right == 0 or abs(drug_index - d_left) < abs(drug_index - d_right):
                        drug_date.append(temp[d_left-1 :drug_index  + 1])
                        drug_dict[temp[drug_index].lower()]['Dosage'] = temp[d_left - 1] + " " + temp[d_left]

                d_left = 0 
                d_right = 0 
                left = 0 
                right = 0 
                
            elif drug[i2].lower() + ' ' in slpit[i1]:
                drug_index = temp.index(drug[i2].split()[0].lower())
                for i5 in range(len(time_label)):
                    for i3 in range(drug_index-1, -1, -1):
                        if time_label[i5] == temp[i3]:
                            left = i3
                            break
                    for i4 in range(drug_index, len(temp)):
                        if time_label[i5] == temp[i4]:
                            right = i4
                            break

                for i5 in range(len(amount)):
                    for i3 in range(drug_index-1, -1, -1):
                        if amount[i5] in temp[i3]:
                            d_left = i3
                            break
                    for i4 in range(drug_index, len(temp)):
                        if amount[i5] in temp[i4]:
                            d_right = i4
                            break

                if left != 0 or right != 0:
                    if left == 0 or abs(drug_index - left) >= abs(drug_index - right):
                        drug_date.append(temp[drug_index : right + 1])
                        drug_dict[temp[drug_index]]['Duration'] = temp[right - 1] + " " + temp[right]
                    elif right == 0 or abs(drug_index - left) < abs(drug_index - right):
                        drug_date.append(temp[left-1 :drug_index  + 1])
                        drug_dict[temp[drug_index]]['Duration'] = temp[left - 1] + " " + temp[left]
                if d_left != 0 or d_right != 0:
                    if d_left == 0 or abs(drug_index - d_left) >= abs(drug_index - d_right):
                        drug_date.append(temp[drug_index : d_right + 1])
                        drug_dict[temp[drug_index].lower()]['Dosage'] = temp[d_right - 1] + "  " + temp[d_right]
                    elif d_right == 0 or abs(drug_index - d_left) < abs(drug_index - d_right):
                        drug_date.append(temp[d_left-1 :drug_index  + 1])
                        drug_dict[temp[drug_index]]['Dosage'] = temp[d_left - 1] + " " + temp[d_left]

                d_left = 0
                d_right = 0
                left = 0
                right = 0
    #print(drug_dict)
######################################################################
#밑에 코드는 queue써서 ArmgroupDescription쪽에서 기간관련 내용 찾는 코드(폐기각)
######################################################################




######################################################################
#밑에 코드는 queue써서 intervention쪽에서 기간관련 내용 찾는 코드(폐기각)
######################################################################

    # protocolsection = response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']

    # for value in protocolsection['ArmsInterventionsModule']['InterventionList']['Intervention']:
    #     value_line = value['InterventionDescription'].split('. ')
    #     for line in value_line:
    #         temp = line.split()
    #         for i2 in drug_dict:
    #             for i1 in range(len(temp)):
    #                 if (temp[i1] in i2):
    #                     dosage_que.put(temp[i1])
    #                 for i3 in amount:
    #                     if i3 in temp[i1]:
    #                         dosage_que.put( temp[i1-1] + temp[i1])
    # for i in range(dosage_que.qsize()):
    #     print(dosage_que.get())


######################################################################
#밑에 코드는 comprehend써서 intervention쪽에서 복용량, 기간 찾는 코드#
######################################################################
    #comprehend = boto3.client('comprehend')

    protocolsection = response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']


    for value in protocolsection['ArmsInterventionsModule']['InterventionList']['Intervention']:
        for i in drug_dict:
            drug_dict[i.lower()]['DrugName'] = i.lower() 
            if i == value["InterventionName"].lower():
                try:
                    DetectEntitiestext = value['InterventionDescription']
                    test = (comprehend.detect_entities(Text=DetectEntitiestext, LanguageCode='en'))
                    for i2 in range(len(test['Entities'])):
                        if(test['Entities'][i2]['Type'] == "QUANTITY"):
                            for k in range(len(amount)):
                                if (amount[k] in test['Entities'][i2]['Text']):
                                    drug_dict[i.lower()]['Dosage'] = test['Entities'][i2]['Text']
                                # drug_dict[i.lower()]['Dosage'] = drug_dict[i.lower()]['Dosage'] + " " + test['Entities'][i2]['Text'] 다시한번 생각해 봐야할 듯
                        for j in range(len(time_label2)):
                            if time_label2[j] in test['Entities'][i2]['Text']:
                                drug_dict[i.lower()]['Duration'] = test['Entities'][i2]['Text']
                except KeyError:
                    pass
    #print(drug_dict)

    #print(drug_dict)
########################################################################################
#밑에 코드는 ACM써서 인터벤션 디스크립션 부분에서 약물 복용법, 복용 주기 관련 내용 추출#
########################################################################################
    #comprehend_med = boto3.client(service_name='comprehendmedical')

    for value in protocolsection['ArmsInterventionsModule']['InterventionList']['Intervention']:
        for i in drug_dict:
            drug_dict[i.lower()]['DrugName'] = i.lower() 
            if i == value["InterventionName"].lower():
                try:
                    DetectEntitiestext = value['InterventionDescription']
                    test = (comprehend_med.detect_entities(Text=DetectEntitiestext)) 
                    for i2 in range(len(test['Entities'])):
                        try:
                            for i3 in range(len(test['Entities'][i2]['Attributes'])):
                                if test['Entities'][i2]['Attributes'][i3]['Type'] == "ROUTE_OR_MODE":
                                    drug_dict[i.lower()]['HowToTake'] = test['Entities'][i2]['Attributes'][i3]['Text'] 
                                elif test['Entities'][i2]['Attributes'][i3]['Type'] == "Duration":
                                    drug_dict[i.lower()]['Duration'] = test['Entities'][i2]['Attributes'][i3]['Text']
                        except KeyError:
                            pass
                except KeyError:
                    pass
#################################################################################################
#밑에 코드는 ACM써서 디스크립션 부분에서 약물 복용 주기 내용 찾는 코드(무조건 마지막에 나와야함)#
#################################################################################################
    #comprehend_med = boto3.client(service_name='comprehendmedical')

    DetectEntitiestext = brief_description + ' ' + detail_description
    result = comprehend_med.detect_entities(Text=DetectEntitiestext)
    entities = result['Entities']
    for value in entities:
        try:
            for content in value['Attributes']:
                if content['RelationshipType'] == "FREQUENCY":
                    for content2 in drug_dict:
                        if value["Text"] in content2:
                            drug_dict[content2]['Duration'] = drug_dict[content2]['Duration'] +"("+ content['Text'] + ")"
        except KeyError:
            pass

    for arm in Arm_group:
        try:
            for DrugName in Arm_group[arm]['InterventionList']['ArmGroupInterventionName']:
                for DrugInList in drug_dict:
                    temp = DrugName.split()
                    # print(temp)
                    # print(" ".join(temp[1:]))





                    if DrugInList == " ".join(temp[1:]).lower():
                        Arm_group[arm]['InterventionDescription'].append(drug_dict[DrugInList]) 
        except TypeError:
            pass
                    #Arm_group[arm]['InteventionDescription'][DrugInList] = ("'" + DrugInList + "'" + ": "+  "{" + drug_dict[DrugInList] + "}")
                    #Arm_group[arm]['InteventionDescription'][DrugInList] = drug_dict[DrugInList]

    for arm in Arm_group:
        try:
            for Drugidx in range(len(Arm_group[arm]['InterventionDescription'])):
                Arm_group[arm]['ArmGroupDescription'] = Arm_group[arm]['ArmGroupDescription'] + Arm_group[arm]['InterventionDescription'][Drugidx]['DrugName']  + ': '  +  Arm_group[arm]['InterventionDescription'][Drugidx]['Dosage'] + ' ' + Arm_group[arm]['InterventionDescription'][Drugidx]['Duration'] + ' ' + Arm_group[arm]['InterventionDescription'][Drugidx]['HowToTake']
                Arm_group[arm]['ArmGroupDescription'] += ', '

        except KeyError:
            pass

    for key in Arm_group:
        InterventionDrug['ArmGroupList'].append(Arm_group[key])

    return_dictionary = {"DrugInformation" : InterventionDrug}
    return return_dictionary


#################################################################################################################################################
#################################################################################################################################################
#################################################################################################################################################
def get_population_ratio(response):

    #test example 1 with n=~ https://www.clinicaltrials.gov/ct2/show/NCT03507790?recrs=ab&type=Intr&cond=Alzheimer+Disease&draw=2
    #test example 2 without n=~ https://www.clinicaltrials.gov/ct2/show/NCT02285140?term=factorial&draw=3

    #save the detail of armDescription
    population_list, save_value, rate, rateString, count = [], [], [], '', 0

    #if there is no "n=~~~"
    #count = 0
    #get the total participates number
    #total = int(response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['DesignModule']['EnrollmentInfo']['EnrollmentCount'])
    #save_total = int(response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['DesignModule']['EnrollmentInfo']['EnrollmentCount'])

    #get the detail of each arm group
    try:
        for i in range(len(response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['ArmsInterventionsModule']["ArmGroupList"]["ArmGroup"])):
            findPopulation = ''.join([str(item) for item in response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['ArmsInterventionsModule']['ArmGroupList']['ArmGroup'][i]['ArmGroupDescription']])
            population_list.append(findPopulation)

        #get the int value of each arm group
        for i in range(len(population_list)):
            #if there is such that matches then meaning there is set ratio
            if "n=" in population_list[i] or "n= " in population_list[i] or "n:" in population_list[i]:
                length_word = len(population_list[i])
                #check if there is word that matches
                start_index=re.search("n=", population_list[i]).start()
                #get the exact value
                extracted_string= population_list[i][start_index:start_index+length_word]
                #print(extracted_string)
                #take out the value of extracted, for example if n=40, get 40 and minus from the total
                save_value.append([int(num) for num in re.findall(r"\d+", extracted_string)][0])

        if count == 0:
            for i in range(len(save_value)):
                rate.append(save_value[i]/math.gcd(*save_value))
            rateString =str(rate[0])
            for i in range(1,len(rate)):
                rateString = rateString +" : " +str(rate[i])

        else:
            #just up up the total
            count += 1
            
    except:
        population_list.append("")


    return_population_ratio_dictionary = {"PopulationRatio" : rateString}
    return return_population_ratio_dictionary


#################################################################################################################################################
#################################################################################################################################################
#################################################################################################################################################
def get_washout(response):
    period = ['washout','wash-out','recovery','run-in']
    times = ['day','days','week','weeks','month','months','year','years']
    line = ""
    index, value = [], []
    min_index, hasWash, hasTime, min = 0, 0, 0, 100

    # washout이 어디에 있는지 확인하고 split하기
    for i in range(len(period)):
            try:
                for j in range(len(response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['ArmsInterventionsModule']['InterventionList']['Intervention'])):
                    content = response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['ArmsInterventionsModule']['InterventionList']['Intervention'][j]['InterventionDescription']
                    content = content.lower()
                    if(period[i] in content):
                        content_list = content.split('.')
                        hasWash += 1
                        break
            except:
                pass
            try:
                for j in range(len(response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['ArmsInterventionsModule']['ArmGroupList']['ArmGroup'])):
                    content = response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['ArmsInterventionsModule']['ArmGroupList']['ArmGroup'][j]['ArmGroupDescription']
                    content = content.lower()
                    if(period[i] in content):
                        content_list = content.split('\n')
                        hasWash += 1
                        break
            except:
                pass

    if (hasWash == 0):
        for i in range(len(period)):
            try:
                content = response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['DescriptionModule']["BriefSummary"]
                content = content.lower()
                if(period[i] in content):
                   content_list = content.split('.')
                   hasWash += 1
                   break
            except:
                content = response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['EligibilityModule']['EligibilityCriteria']
                content = content.lower()
                if(period[i] in content):
                   content_list = content.split('\n')
                   hasWash += 1
                   break

    # washout 없는 경우
    if(hasWash == 0):
        return {"WashoutPeriod" : ""}

    #washout 있는 line만 추출
    for i in range(len(content_list)):
        for j in range(len(period)):
            if(period[j] in content_list[i]):
                line = content_list[i]
                #washout_index = line.index('period') #period관련 단어의(첫 알파벳) index파악--times 뽑기 위해서
                line_list = line.split(" ")
                washout_index = line.index(period[j]) + 5 #-> washout으로 인덱싱
                washout_index_check = line_list.index(period[j])
                #print(line_list[washout_index-1])

    #without washout period 잡기
    if(line_list[washout_index_check -1]=='without'):
        return {"WashoutPeriod" : ""}
                # if('without' in line):
                #     return {"washout_period" : ""} #without있는 문장 제외(수정 필요)
                # else:
                #     washout_index = line.index(period[j]) #period관련 단어의(첫 알파벳) index파악--times 뽑기 위해서

    #comprehend 돌리기
    #comprehend = boto3.client('comprehend') #주석 하기!!
    DetectEntitiestext = line
    test = (comprehend.detect_entities(Text=DetectEntitiestext, LanguageCode='en'))
    convert = json.dumps(test,sort_keys=True, indent=4)
    data = json.loads(convert)

    # Quantitiy 안에 times 있는지 있으면 뽑기
    for i in range(len(test['Entities'])):
        if(test['Entities'][i]['Type'] == "QUANTITY"):
            for j in range(len(times)):
                if (times[j] in test['Entities'][i]['Text']): #2-week, 4-week
                    index.append(line.index(test['Entities'][i]['Text']))
                    value.append(test['Entities'][i]['Text'])
                    hasTime += 1
    
    if(hasTime == 0):
        return {"WashoutPeriod" : ""}

    # period 표현과 가장 가까운 시간표현 뽑기
    for i in range(len(index)):
        if(min > abs(washout_index - index[i])):
            min = abs(washout_index - index[i])
            min_index = i
    
    #dic형태로 json파일 생성
    string_result = value[min_index]
    change_dictionary = "{%s : %s%s%s}" % ('"WashoutPeriod"', '"', string_result, '"')
    result_dictionary = json.loads(change_dictionary)
    return(result_dictionary)

#################################################################################################################################################
#################################################################################################################################################
#################################################################################################################################################
def get_officialTitle(response):
    title = response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['IdentificationModule']['OfficialTitle']
    string_result = title
    change_dictionary = "{\"OfficialTitle\" : " + '"' + string_result + '"' + "}"
    result_dictionary = json.loads(change_dictionary)
    return(result_dictionary)


#################################################################################################################################################
#################################################################################################################################################
#################################################################################################################################################
def get_objective(response):
    summary = response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['DescriptionModule']["BriefSummary"]
    purpose = ['objective', 'purpose', 'aim', 'evaluate', 'measure', 'intention', 'target', 'goal', 'object', 'idea', 'desire']
    list = summary.split('.')

    # 보기에는 없어도 api에는 BriefTitle이 있는 경우가 많음
    if("BriefTitle" in response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['IdentificationModule']):
        objective = response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['IdentificationModule']["BriefTitle"]

    # 혹시 모를 예외 케이스를 위해 BriefSummary에 목적의 표현이 있는 문장 추출
    else:
        for i in range(len(list)):
            for j in range(len(purpose)):
                if(list[i] == purpose[j]):
                    objective = list[i]
                    break

    string_result = objective
    change_dictionary = "{\"Objective\" : " + '"' + string_result + '"' + "}"
    result_dictionary = json.loads(change_dictionary)
    return(result_dictionary)


#################################################################################################################################################
#################################################################################################################################################
#################################################################################################################################################
def get_maksing(response):
    masking = response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['DesignModule']['DesignInfo']['DesignMaskingInfo']['DesignMasking']
    string_result = masking
    change_dictionary = "{\"Masking\" : " + '"' + string_result + '"' + "}"
    result_dictionary = json.loads(change_dictionary)
    return(result_dictionary)


#################################################################################################################################################
#################################################################################################################################################
#################################################################################################################################################
def get_allocation(response):
    allocation = response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['DesignModule']['DesignInfo']['DesignAllocation']
    string_result = allocation
    change_dictionary = "{\"Allocation\" : " + '"' + string_result + '"' + "}"
    result_dictionary = json.loads(change_dictionary)
    return(result_dictionary)


#################################################################################################################################################
#################################################################################################################################################
#################################################################################################################################################
def get_enrollment(response):
    enrollment = response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['DesignModule']['EnrollmentInfo']['EnrollmentCount']
    string_result = enrollment
    change_dictionary = "{\"Enrollment\" : " + '"' + string_result + '"' + "}"
    result_dictionary = json.loads(change_dictionary)
    return(result_dictionary)


#################################################################################################################################################
#################################################################################################################################################
#################################################################################################################################################
def get_designModel(response):
    model = response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['DesignModule']['DesignInfo']['DesignInterventionModel']
    string_result = model
    change_dictionary = "{\"DesignModel\" : " + '"' + string_result + '"' + "}"
    result_dictionary = json.loads(change_dictionary)
    return(result_dictionary)


#################################################################################################################################################
#################################################################################################################################################
#################################################################################################################################################
def get_interventionName(response):
    interventionName = []
    type = ""
    
    for i in range(len(response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['ArmsInterventionsModule']['InterventionList']['Intervention'])):
        type = response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['ArmsInterventionsModule']['InterventionList']['Intervention'][i]['InterventionType']
        name = response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['ArmsInterventionsModule']['InterventionList']['Intervention'][i]['InterventionName']
        if ('Placebo' in name):
            interventionName.append(name)
        elif ('+' in name):
            interventionName.append(name)
        elif(type=="Drug"):
            DetectEntitiestext = name
            test = (comprehend_med.detect_entities(Text=DetectEntitiestext))
            convert = json.dumps(test,sort_keys=True, indent=4)
            data = json.loads(convert)
            for j in range(len(test['Entities'])):
                if(test['Entities'][j]['Type']== 'ID'):
                    interventionName.append(test['Entities'][j]['Text'])
                elif(test['Entities'][j]['Type']=='GENERIC_NAME'):
                    interventionName.append(test['Entities'][j]['Text'])
        else:
            interventionName.append(name)
    # list -> string하면서 ', ' 넣기
    string_result = ', '.join(interventionName)
    change_dictionary = "{%s : %s%s%s}" % ('"InterventionName"', '"', string_result, '"')
    result_dictionary = json.loads(change_dictionary)
    return(result_dictionary)


#################################################################################################################################################
#################################################################################################################################################
#################################################################################################################################################
#################################################################################################################################################
#################################################################################################################################################
#################################################################################################################################################
#################################################################################################################################################
#################################################################################################################################################
#################################################################################################################################################
def wrapper(func, arg, queue):
        queue.put(func(arg))

def request_call(url):

    try:
        expr = re.search("NCT[0-9]+", url)
        expr = expr.group()
        if((expr == None) or ("&fmt=json" in url)):
            newURL = url
        else:
            newURL = "https://clinicaltrials.gov/api/query/full_studies?expr=" + expr + "&fmt=json"
    except:
        newURL = url.replace(" ", "")

    response = requests.get(newURL).json()

    NCTId = {"NCTID" : response['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['IdentificationModule']['NCTId']}

    washout, drug_time, population_box = Queue(), Queue(), Queue()
    Thread(target=wrapper, args=(get_washout, response, washout)).start() 
    Thread(target=wrapper, args=(get_drug_time, response, drug_time)).start() 
    Thread(target=wrapper, args=(get_population_box, response, population_box)).start() 

    #dictionary format
    calc_date, population_ratio, official_title, objective, allocation, enrollment, design_model, masking, intervention_name, title = get_calc_date(response), get_population_ratio(response), get_officialTitle(response), get_objective(response), get_allocation(response), get_enrollment(response), get_designModel(response), get_maksing(response), get_interventionName(response), get_title(response)

    request_call = {}
    request_call.update(title)
    request_call.update(population_box.get())
    request_call.update(washout.get())
    request_call.update(population_ratio)
    request_call.update(calc_date)
    request_call.update(drug_time.get())
    request_call.update(official_title)
    request_call.update(objective)
    request_call.update(allocation)
    request_call.update(enrollment)
    request_call.update(design_model)
    request_call.update(masking)
    request_call.update(intervention_name)
    request_call.update(NCTId)



    #print(request_call['population_ratio'])

    with open("resource_control.json", 'w') as json_file:
            json.dump(request_call, json_file,sort_keys=True, indent=4)

    return request_call