import re

'''
parseQuestions(): parses query.txt file and creates 2 data structures, a questions dictionary
keyed by linenumber and contains a list with the question and response; parse variable names from
query.txt into a list
'''

def parseQuestions():
    questions = {}
    variables = []
    i = 0
    f = open("query.txt","r")
    for line in f.readlines():
        i += 1
        if "A1" in line:
            cols = line.split("|")
            q = cols[1]
            a = cols[2]
            questions[i] = [q, a[:-1]]
        else:
            if line != "\n":
                var = re.search(".*(?=:)", line).group(0)
                variables.append(var[1:-1])
    return questions, variables

'''
parseQuery(): parses the input question and returns a dictionary containing a signal 
(normal, unknown, question, end, error etc), and returns a dictionary of signals and
(if normal) the question number and variables associated with it
'''

def parseQuery(input, questions):
    # return something something
    return {"signal": "End"}
