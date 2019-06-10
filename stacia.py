import sys
import queryparser

query = ""
name = ""
endsignal = 0
question, variable = queryparser.parseQuestions()
classifier = queryparser.createModel(question)
print("   _____ _         _____ _____          \n  / ____| |       / ____|_   _|   /\    \n | (___ | |_ __ _| |      | |    /  \   \n  \___ \| __/ _` | |      | |   / /\ \  \n  ____) | || (_| | |____ _| |_ / ____ \ \n |_____/ \__\__,_|\_____|_____/_/    \_\ \n")
print("Welcome to the StaCIA Bot to help with your questions on")
print("tutoring and clubs for both CSSE and STAT in Cal Poly!")
print("\nFirst things first, let's get to know eachother! What's your name?")
name = input("> ").strip()
print("Nice to meet you " + name + "! Let's get started.")
print("\nEnter your question " + name + ", and I'll be happy to provide you an answer! Just tell me bye when you're done!")
while endsignal == 0:
    query = input("> ").strip()
    if "bye" in query.lower():
        endsignal = 1
    parsedQuery = queryparser.parseQuery(query, question, classifier)
    if parsedQuery["signal"] == "End":
        endsignal = 1
    print(parsedQuery) # just for now
    # response = getanswer(parsedQuery)
    # print(response)
print("\nGoodbye " + name + "! See you again soon!")



