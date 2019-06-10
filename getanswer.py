import pymysql.cursors, time,re, requests, random, os, sys

f = open("credentials.txt","r")
if f.mode == 'r':
    database = f.readline()
    pwd = f.readline()
    fbuser = f.readline()
    fbpwd = f.readline()

connection = pymysql.connect(host='localhost',
                             user=database.rstrip(" \n"),
                             password=pwd.rstrip(" \n"),
                             db=database.rstrip(" \n"),
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

# store all the mysql query into a list 
def listOfQuery():
    f = open("mysql.txt","r")
    querylist = []
    for line in f.readlines():
        if "\n" in line:
            querylist.append(line[:-1])

    return querylist

# helper function 
def replace_first_bracelet(response, word):
   splited = response.split('[', 1)
   response = splited[0] + word + splited[1].split(']', 1)[1]
   return response

def replace_response_with_list(response, word_list):
   for word in word_list:
      response = replace_first_bracelet(response, word)
   return response

# give a native response to a question that we know the answer
def normal_answer(query, questions):

    question_num = query["question"]
    question_var = query["variables"] # a dictionary in the format {“varname”: [variable taken from the input query]}
    listofkeys = list(question_var) # a list of variable names
    print(listofkeys)
    listofquery = listOfQuery() # a list of mysql query in the order of the questions
    sql = listofquery[question_num-1] # the sql command for the query
    response = questions[question_num][1] # the response format from the question dictionary

    for item in listofkeys:
        if item in sql:
            sql = sql.replace(item, question_var[item]) #should be a whole sql command after replace
            print(sql)
        if item in response:
            response = response.replace('['+item+']', question_var[item])
            print(response)

    # count number of varibales in the response are coming from tables
    cnt = 0
    for char in response:
        if char == '[':
            cnt += 1

    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)

            if cnt == 1 : 
                result = ''
                res = response.split('[')
                for row in cursor:
                    result += str(row[(cursor.description)[0][0]]) + ', '
                result = result[:-2]
                response = res[0] + result + response.split(']')[1] 

            elif cnt == 2:
                result = []

                for row in cursor:
                    result.append(str(row[(cursor.description)[0][0]]))

                response = replace_response_with_list(response, result)
          
                

    except BaseException as e:
       return "Sorry, I don't know the answer to this!"

    return response
    
def getanswer(query, question):
    
    response_string = ''

    if query['signal'] == 'Normal':
        response_string = normal_answer(query, question)

    elif query['signal'] == 'Unknown':
        response_string = "Sorry, I don't know the answer to this!"

    elif query['signal'] == 'End':
        response_string = 'Glad to help you today! Goodbye!'

    return response_string
