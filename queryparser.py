import re
import nltk

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
    f.close()
    return questions, variables

'''
parseQuery(): parses the input question and returns a dictionary containing a signal 
(normal, unknown, question, end, error etc), and returns a dictionary of signals and
(if normal) the question number and variables associated with it
'''

def parseQuery(input, questions, classifier):
    label = classifier.classify(getFeatures(input.lower()))
    probs = classifier.prob_classify(getFeatures(input.lower()))
    probLabel = probs.prob(label)
    print(label)
    print(probLabel)
    print(questions[label])
    if probLabel < .1:
        return {"signal":"Unknown"}
    else:
        parsed = {"signal": "Normal", "question":label}
        variable = {}
        inputSplit = input.split(" ")
        detQuestion = questions[label][0].split(" ")
        idq = 0
        iis = 0
        var = ""
        varname = ""
        stop = ""
        while iis < len(inputSplit) and idq < len(detQuestion):
            if "[" in detQuestion[idq] and "]" in detQuestion[idq]:
                varname = detQuestion[idq][1:-1]
                if "]" in varname:
                    varname = varname[:-1]
                idq += 1
                if idq >= len(detQuestion):
                    var = " ".join(inputSplit[iis:])[:-1]
                else:
                    stop = detQuestion[idq].lower()
                    while iis < len(inputSplit) and stop not in inputSplit[iis].lower():
                        var += inputSplit[iis] + " "
                        iis += 1
                variable[varname] = var.strip()
                var = ""
                varname = ""
            else:
                iis += 1
                idq += 1
        parsed["variable"] = variable
        return parsed

'''
createModel(): creates and trains a model to classify the question
'''

def createModel(questions):
    labeled = []
    for k, v in questions.items():
        labeled.append((v[0].lower(), k))
    '''
    i = 0
    f = open("train.txt", "r")
    for line in f.readlines():
        i += 1
        split = line.split("|")
        for s in split:
            labeled.append((s.lower(), i))
    f.close()
    '''
    labeled = [(getFeatures(q), num) for (q, num) in labeled]
    classifier = nltk.NaiveBayesClassifier.train(labeled)
    return classifier

'''
getFeatures(): extracts features from the question
'''

def getFeatures(question):
    features = {"who":"who" in question,
                "what":"what" in question,
                "where":"where" in question,
                "when":"when" in question,
                "why":"why" in question,
                "how":"how" in question,
                "are":"are" in question,
                "club":"club" in question,
                "tutor":"tutor" in question,
                "center":"center" in question,
                "offer":"offer" in question,
                "many":"many" in question,
                "number":"number" in question,
                "advise":"advise" in question,
                "advisor":"advisor" in question,
                "email":"email" in question,
                "type":"type" in question,
                "kind":"kind" in question,
                "president":"president" in question,
                "secretary":"secretary" in question,
                "treasurer":"treasurer" in question,
                "homepage":"homepage" in question,
                "page":"page" in question,
                "box":"box" in question,
                "box number":"box number" in question,
                "social":"social" in question,
                "social media":"social media" in question,
                "facebook":"facebook" in question,
                "instagram":"instagram" in question,
                "upcoming":"upcoming" in question,
                "next":"next" in question,
                "follower":"follower" in question,
                "following":"following" in question,
                "account":"account" in question,
                "latest":"latest" in question,
                "post":"post" in question,
                "is":"is" in question,
                "on":"on" in question,
                "does":"does" in question,
                "room":"room" in question,
                "office":"office" in question,
                "officer":"officer" in question,
                "meeting":"meeting" in question,
                "event":"event" in question,
                "meet":"meet" in question,
                "project":"project" in question,
                "sponsor":"sponsor" in question,
                "technical track":"technical track" in question,
                "department":"department" in question,
                "past":"past" in question,
                "contact":"contact" in question,
                "name":"name" in question,
                "reach":"reach" in question,
                "phone":"phone" in question,
                "resource":"resource" in question,
                "together":"together" in question,
                "have":"have" in question,
                "WISH":"WISH" in question,
                "fee":"fee" in question,
                "due":"due" in question,
                "available":"available" in question,
                "begin":"begin" in question,
                "start":"start" in question,
                "end":"end" in question,
                "finish":"finish" in question,
                "head":"head" in question,
                "get":"get" in question,
                "week":"week" in question,
                "csse":"csse" in question,
                "stat":"stat" in question,
                "computer":"computer" in question,
                "science":"science" in question,
                "program":"program" in question,
                "speak":"speak" in question,
                "be":"be" in question,
                "sign":"sign" in question,
                "requirement":"requirement" in question,
                "private":"private" in question,
                " r ": " r " in question,
                "information":"information" in question,
                "assistance":"assistance" in question,
                "help":"help" in question,
                "schedule" : "schedule" in question,
                "locate" : "locate" in question,
                "data":"data" in question,
                "service":"service" in question,
                "peer":"peer" in question,
                "assistant":"assistant" in question,
                "become":"become" in question,
                "people":"people" in question,
                "working":"working" in question,
                "with":"with" in question,
                "sign-up":"sign-up" in question,
                "free":"free" in question,
                "subscription":"subscription" in question,
                "need":"need" in question,
                "require":"require" in question,
                "option":"option" in question,
                "can" :"can" in question,
                "do" : "do" in question
    }
    return features