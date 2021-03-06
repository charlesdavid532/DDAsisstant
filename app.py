from __future__ import print_function
import json
import os, sys, json, requests
from flask import Flask, request, make_response
from flask import jsonify
from flask.ext.pymongo import PyMongo
from pymessenger import Bot
from datetime import datetime as dt
from PIL import Image
from bson.objectid import ObjectId

try:
    import apiai
except ImportError:
    sys.path.append(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
    )
    import apiai

app = Flask(__name__)

# Client Access Token for accessing our API AI Bot TODO: CHANGE THIS
CLIENT_ACCESS_TOKEN = '3247ff63352c4dabada31aea2655398d'

# This seems waste
PAGE_ACCESS_TOKEN = "EAABlZAhiLCzsBAEPENnZC43ODWjX1X4VT43TBjHP8dx8WC7W6kqVRLiRz5AljcmkxSk1rfD2ZA4dDdE149D8JIurZBM67Afl6MRFyZBmqH55mTbJTSbHAjKlHSQrHGITB129ekYkdLqGb2ZBJnN7vyEH4HjgPiXzZAO0yW9wj3WXwZDZD"

# An endpoint to ApiAi, an object used for making requests to a particular agent.
ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)


bot = Bot(PAGE_ACCESS_TOKEN)

app.config['MONGO_DBNAME'] = 'temp'
app.config['MONGO_URI'] = 'mongodb://admin:admin@ds145892.mlab.com:45892/temp'
app.config['ASSIST_ACTIONS_ON_GOOGLE'] = True

mongo = PyMongo(app)


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

'''
@app.route('/')
def index():
    return 'Hello world!'
'''

@app.route('/', methods=['GET'])
def verify():
    print ("Hellow world")
	# Webhook verification
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == "hello":
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200
    return "Hello world I am Charles", 200



# Handling HTTP POST when APIAI sends us a payload of messages that have
# have been sent to our bot. 
@app.route('/webhook', methods=['POST'])
def handle_message():
    data = request.get_json()
    print("Request:")
    print(json.dumps(data, indent=4))
    res = processRequest(data)

    res = json.dumps(res, indent=4, cls=JSONEncoder)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    print("Before final return")
    return r

    


def processRequest(req):
    print('hi')
    if req.get("result").get("action") == "sales.statistics":
        myCustomResult = getParameters(req)
        res = makeWebhookResult(myCustomResult)
    elif req.get("result").get("action") == "welcome.intent":
        res = showWelcomeIntent(req)
    elif req.get("result").get("action") == "showAllUsers":
        res = makeListOfAllUsers(req)
    elif req.get("result").get("action") == "detailed.bio":
        res = showDetailedBio(req)
    elif req.get("result").get("action") == "application.close":
        res = closeApplication(req)
    elif req.get("result").get("action") == "application.help":
        res = showHelpScreen(req)    
    elif req.get("result").get("action") == "time.timeperiod":
        ''' TODO REMOVE temp
        myCustomResult = getDummyParameters(req)
        res = makeWebhookResult(myCustomResult)
        '''
        return {}
    else:
        return {}
    return res
'''
This is a very temp function. It is used to just create a sample response in JSON format
'''
def makeWebhookResult(data):
    speech = data
    '''
    print("Response:")
    print(speech)
    '''
    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "DDAsisstant"
    }
    
def itemSelected(app):
    # Get the user's selection
    param = app.getContextArgument('actions_intent_option','OPTION').value
    print ("There is no chance it comes here")

def showWelcomeIntent(resp):
    print ("Inside show welcome intent")

    return createCardResponse(["Hi, I am Doctor Digital, your very own Deloitte Digital Assistant! The suggestions below are some of the things I can do! At any time if you want to leave the application say Bye doctor digital! What can I do for you?"], 
        ["Show digital employees", "Bye doctor digital"], 
        "Dr. Digital", "DDAssistant a.k.a. Dr. Digital is designed to help map employees of Deloitte Digital to the upcoming projects.", "", 
        "https://s3.ap-south-1.amazonaws.com/tonibot-bucket/blue-bot.png", "Default accessibility text", [], [], True)


def closeApplication(req):
    print("closing application")

    return createCardResponse(["It was a pleasure serving you!"], [], 
        "Dr. Digital", "Hope to see you again soon!", "", 
        "https://s3.ap-south-1.amazonaws.com/tonibot-bucket/blue-bot.png", "Default accessibility text", [], [], False)

def showHelpScreen(req):
    print("displaying help")

    return createCardResponse(["Let me help you out! The suggestions below are some of the things I can do! At any time if you want to leave the application say Bye doctor digital! What can I do for you?"], ["Show digital employees", "Bye doctor digital"], 
        "Dr. Digital", "DDAssistant a.k.a. Dr. Digital is designed to help map employees of Deloitte Digital to the upcoming projects.", "", 
        "https://s3.ap-south-1.amazonaws.com/tonibot-bucket/blue-bot.png", "Default accessibility text", [], [], True)

def showDetailedBio(req):
    print("wow")
    print("before the argument parameter")
    firstInput = req["originalRequest"]["data"]["inputs"][0]
    if 'arguments' in firstInput:
        optionVal = firstInput["arguments"][0]["textValue"]
        print(optionVal)
        
        baseUrl = "https://s3.ap-south-1.amazonaws.com/tonibot-bucket/"
        tempData = mongo.db.temp1
        try: 
            for s in tempData.find({'_id': ObjectId(optionVal)}):
                fullName = s['name']
                print ("The name is:" + s['name'])
                designation = s['designation']
                bio = s['bio']
                photoUrl = baseUrl + s['photo']
                profilePhoto = photoUrl

        except Exception:
            print("Could not query database")
            return makeWebhookResult('This name does not exist in the list! Say show digital employees to show all employees or say Bye doctor digital to exit')


        return createCardResponse(["The detailed bio of " + fullName, "Click on any one of the suggestions below or say Bye doctor digital to exit!"], ["Show digital employees", "Bye doctor digital"], 
            fullName, bio, designation, 
            profilePhoto, "Default accessibility text", [], [], True)
    else:
        print("In the else part of detailed bio")
        return makeWebhookResult('This name does not exist in the list! Say show digital employees to show all employees or say Bye doctor digital to exit')


def makeListOfAllUsers(resp):
    '''
    resp.card(text='Dummy Card',title='Card title',img_url='https://drive.google.com/open?id=0BzU--BJmmVjua0dSVnZNYVJCLXc')

    return resp
    '''
    print("Inside make card")
    '''
    return {
        "simpleResponse": {
                                "textToSpeech": "Math and prime numbers it is!"
                            },
        "basicCard": {
                                "title": "Math & prime numbers",
                                "formattedText": "42 is an even composite number. It \n      is composed of three distinct prime numbers multiplied together. It \n      has a total of eight divisors. 42 is an abundant number, because the \n      sum of its proper divisors 54 is greater than itself. To count from \n      1 to 42 would take you about twenty-one…",
                                "image": {
                                    "url": "https://drive.google.com/open?id=0BzU--BJmmVjua0dSVnZNYVJCLXc",
                                    "accessibilityText": "Image alternate text"
                                },
                                "buttons": []
                            }
    }
    
    return {
        "simpleResponse": {
                                "textToSpeech": "Howdy! I can tell you fun facts about almost any number, like 42. What do you have in mind?",
                                "displayText": "Howdy! I can tell you fun facts about almost any number. What do you have in mind?"
                            },
         "source": "DDAsisstant"
    }
    '''

    # This is the database query to fetch the appropriate data (TODO: Move to another function)
    fullName = []
    designation = []
    bio = []
    profilePhoto = []
    keys = []
    baseUrl = "https://s3.ap-south-1.amazonaws.com/tonibot-bucket/"
    tempData = mongo.db.temp1
    try: 
        for s in tempData.find():
            keys.append(s['_id'])
            fullName.append(s['name'])
            print ("The name is:" + s['name'])
            designation.append(s['designation'])
            bio.append(s['bio'])
            photoUrl = baseUrl + s['photo']
            profilePhoto.append(photoUrl)

    except Exception:
        print("Could not query database")
        return makeWebhookResult('This name does not exist in the list!')
    
    print("Before opening image")
   
    #createImage()

    print("Before printing list item")
    #print(json.dumps(createListItem(fullName,fullName,designation,"https://developers.google.com/actions/images/badges/XPM_BADGING_GoogleAssistant_VER.png"), indent=4))
    #print(json.dumps(createListResponse("My sample response",["sug1","sug2"],"My list title",[fullName, "Charlie"],[fullName, "Dans"],[designation, "Cons"],["https://developers.google.com/actions/images/badges/XPM_BADGING_GoogleAssistant_VER.png","https://developers.google.com/actions/images/badges/XPM_BADGING_GoogleAssistant_VER.png"]), indent=4))

    return createListResponse(["Here are the employees of Deloitte Digital. Click on any one of them or say their names to view their detailed bio"],[],"DD Resources", keys, fullName, fullName, designation, profilePhoto, False)
    '''
    return {
        "speech": "Howdy",
        "displayText": "Howdy",
        "data": {
          "google": {
          "expect_user_response": True,
          "rich_response": {
          "items": [
            {
              "simpleResponse": {
                  "textToSpeech":"Here are all the employees of Deloitte Digital"
              }
            },
            {
              "basicCard": {
                "title":fullName,
                "formattedText":"Charles is an MBA from NMIMS",
                "subtitle":designation,
                "image": {
                  "url":"https://developers.google.com/actions/images/badges/XPM_BADGING_GoogleAssistant_VER.png",
                  "accessibilityText":"Image alternate text"
                },
                "buttons": [
                  {
                    "title":"View Profile",
                    "openUrlAction":{
                      "url":"https://assistant.google.com/"
                    }
                  }
                ]
              }
            }
          ],
          "suggestions":
          [
            {"title":"I have a new project"},
            {"title":"Search people with skills"}
          ]
        }
        }
        },
         #"contextOut": [],
        "source": "DDAsisstant"
    }
    '''
    '''
    return {
        "speech": "Howdy",
        "displayText": "Howdy",
        "data": {
          "google": {
          "expect_user_response": True,
          "rich_response": {
          "items": [
                {
                    "simpleResponse": {
                        "textToSpeech":"This is a simple response for a list"
                    }
                }
            ],
            "suggestions": [
                {
                    "title":"List"
                },
                {
                    "title":"Carousel"
                },
                {
                    "title":"Suggestions"
                }
            ]
        },
        "systemIntent": {
            "intent":"actions.intent.OPTION",
            "data": {
                "@type" : "type.googleapis.com/google.actions.v2.OptionValueSpec",
                "listSelect": {
                    "title":"List Title","items": [
                        {
                            "optionInfo": {
                                "key":"title",
                                "synonyms": [
                                "synonym of title 1",
                                "synonym of title 2",
                                "synonym of title 3"
                            ]
                        },
                        "title":"Title of First ListItem",
                        "description":"This is a description of a list item",
                        "image": {
                            "url":"https://developers.google.com/actions/images/badges/XPM_BADGING_GoogleAssistant_VER.png",
                            "accessibilityText":"Image alternate text"
                            }
                        },
                        {
                            "optionInfo": {
                                "key":"googleHome",
                                "synonyms": [
                                    "Google Home Assistant","Assistant on the Google Home"
                                ]
                            },
                            "title":"Google Home",
                            "description":"Google Home is a voice-activated speaker powered by the Google Assistant.",
                            "image": {
                                "url":"https://lh3.googleusercontent.com/Nu3a6F80WfixUqf_ec_vgXy_c0-0r4VLJRXjVFF_X_CIilEu8B9fT35qyTEj_PEsKw",
                                "accessibilityText":"Google Home"
                            }
                        },
                        {
                            "optionInfo": {
                                "key":"googlePixel",
                                "synonyms": [
                                    "Google Pixel XL",
                                    "Pixel","Pixel XL"
                                ]
                            },
                            "title":"Google Pixel",
                            "description":"Pixel. Phone by Google.",
                            "image": {
                                "url":"https://storage.googleapis.com/madebygoog/v1/Pixel/Pixel_ColorPicker/Pixel_Device_Angled_Black-720w.png",
                                "accessibilityText":"Google Pixel"
                            }
                        },
                        {
                            "optionInfo": {
                                "key":"googleAllo",
                                "synonyms": [
                                    "Allo"
                                ]
                            },
                            "title":"Google Allo",
                            "description":"Introducing Google Allo, a smart messaging app that helps you say more and do more.",
                            "image": {
                                "url":"https://allo.google.com/images/allo-logo.png",
                                "accessibilityText":"Google Allo Logo"
                            }
                        }
                    ]
                }
            }
        }
        }
        },
         #"contextOut": [],
        "source": "DDAsisstant"
    }
    '''


def createImage():
    image = Image.open('profile.jpg')
    image.show()

'''
This function returns a card response
'''
def createCardResponse(simpleResponse, sugList, title, formattedText, subtitle, imgURL, imgAccText, btnTitleList, btnUrlList, expectedUserResponse):
    cardResponse = {}

    itemsDict = {}
    itemsDict["simpleResponse"] = {}
    simpleResponseDict = itemsDict["simpleResponse"]
    simpleResponseDict["textToSpeech"] = simpleResponse[0]

    basicCardDict = {}
    basicCardDict["basicCard"] = createCard(title, formattedText, subtitle, imgURL, imgAccText, btnTitleList, btnUrlList)

    cardResponse["data"] = {}
    cardResponse["source"] = "DDAsisstant"
    dataDict = cardResponse["data"]

    dataDict["google"] = {}
    googleDict = dataDict["google"]

    googleDict["expect_user_response"] = expectedUserResponse
    googleDict["rich_response"] = {}
    

    richResponseDict = googleDict["rich_response"]
    richResponseDict["items"] = []
    

    itemList = richResponseDict["items"]
    itemList.append(itemsDict)
    itemList.append(basicCardDict)

    if len(simpleResponse) > 1:
        secondItemsDict = {}
        secondItemsDict["simpleResponse"] = {}
        secondSimpleResponseDict = secondItemsDict["simpleResponse"]
        secondSimpleResponseDict["textToSpeech"] = simpleResponse[1]
        itemList.append(secondItemsDict)

    richResponseDict["suggestions"] = createSuggestionList(sugList)

    

    return cardResponse

'''
This function creates a card
'''
def createCard(title, formattedText, subtitle, imgURL, imgAccText, btnTitleList, btnUrlList):
    basicCard = {}

    if title != "":
        basicCard["title"] = title

    basicCard["formattedText"] = formattedText

    if subtitle != "":
        basicCard["subtitle"] = subtitle

    basicCard["image"] = {}

    imageDict = basicCard["image"]
    imageDict["url"] = imgURL
    imageDict["accessibilityText"] = imgAccText

    basicCard["buttons"] = []

    buttonsList = basicCard["buttons"]

    for index in range(len(btnTitleList)):
        buttonsList.append(createButton(btnTitleList[index], btnUrlList[index]))

    return basicCard


def createButton(title, openUrlAction):
    btnDict = {}

    btnDict["title"] = title
    btnDict["openUrlAction"] = {}

    openUrlActionDict = btnDict["openUrlAction"]
    openUrlActionDict["url"] = openUrlAction

    return btnDict
'''
This function creates a single list item to be used for generating the list card item
'''
def createListItem(key, title, syn, description, imgURL):
    listItemDict = {}
    listItemDict["optionInfo"] = {}

    optionInfoDict = listItemDict["optionInfo"]
    optionInfoDict["key"] = key
    optionInfoDict["synonyms"] = []

    synList = optionInfoDict["synonyms"]
    synList.append(syn)

    listItemDict["title"] = title
    listItemDict["description"] = description

    listItemDict["image"] = {}

    imageDict = listItemDict["image"]
    imageDict["url"] = imgURL
    imageDict["accessibilityText"] = "This is a temporary accessibility text"

    return listItemDict


'''
This function creates an entire list that is used for generating the list card
'''
def createList(listTitle, keyArr, titleArr, synArr, descriptionArr, imgUrlArr):
    systemIntentDict = {}
    systemIntentDict["intent"] = "actions.intent.OPTION"
    systemIntentDict["data"] = {}

    dataDict = systemIntentDict["data"]
    dataDict["@type"] = "type.googleapis.com/google.actions.v2.OptionValueSpec"
    dataDict["listSelect"] = {}

    listSelectDict = dataDict["listSelect"]
    listSelectDict["title"] = listTitle
    listSelectDict["items"] = []

    itemList = listSelectDict["items"]

    for index in range(len(titleArr)):
        itemList.append(createListItem(keyArr[index], titleArr[index], synArr[index], descriptionArr[index], imgUrlArr[index]))


    return systemIntentDict


def createListResponse(simpleResponseArr, sugList, listTitle, keyArr, titleArr, synArr, descriptionArr, imgUrlArr, expectedUserResponse):
    listResponse = {}
    itemsDict = {}
    itemsDict["simpleResponse"] = {}
    simpleResponseDict = itemsDict["simpleResponse"]
    simpleResponseDict["textToSpeech"] = simpleResponseArr[0]

    #Code to add multiple simple responses (Seems unwieldy & needs to be better done for a loop)
    if len(simpleResponseArr) > 1:
        itemsDict1 = {}
        itemsDict1["simpleResponse"] = {}
        simpleResponseDict1 = itemsDict1["simpleResponse"]
        simpleResponseDict1["textToSpeech"] = simpleResponseArr[1]

    listResponse["data"] = {}
    listResponse["source"] = "DDAsisstant"
    dataDict = listResponse["data"]

    dataDict["google"] = {}
    googleDict = dataDict["google"]

    googleDict["expect_user_response"] = expectedUserResponse
    googleDict["rich_response"] = {}
    

    richResponseDict = googleDict["rich_response"]
    richResponseDict["items"] = []
    

    itemList = richResponseDict["items"]
    itemList.append(itemsDict)

    if len(simpleResponseArr) > 1:
        itemList.append(itemsDict1)

    richResponseDict["suggestions"] = createSuggestionList(sugList)

    googleDict["systemIntent"] = createList(listTitle, keyArr, titleArr, synArr, descriptionArr, imgUrlArr)

    return listResponse


def createSuggestion(title):
    suggestionDict = {}
    suggestionDict["title"] = title
    return suggestionDict

def createSuggestionList(titleList):
    suggestionList = []
    for index in range(len(titleList)):
        suggestionList.append(createSuggestion(titleList[index]))

    return suggestionList

def getParameters(req):
    result = req.get("result")
    parameters = result.get("parameters")
    city = parameters.get("city")
    print("The city is:")
    print(city)
    '''
    duration = parameters.get("Duration")
    print("The duration is:")
    print(duration)
    sales = queryData(city, duration)
    '''
    period = parameters.get("period")
    print("The period is:")
    print(period)
    sales = parsePeriod(period, city)
    print("The sales are:")
    print(sales)
    
    '''return "The sales data for " + city + "and duration" + duration + "is 12345"'''
    return "The sales data for " + city + " and duration is " + sales
    '''return "abcd"'''

'''
TODO: REMOVE
'''
def getDummyParameters(req):
    result = req.get("result")
    parameters = result.get("parameters")
    period = parameters.get("period")
    print("The period is:")
    print(period)
    amount = parsePeriod(period)
    
    return "The amount for this duration is " + amount
    

def parsePeriod(period, city):
    '''print ("Period at index 0 is:" + period[0])'''
    '''print ("trying to get date at index 0" + period[0].get('date'))'''
    if period.get('date') != None:
        return queryDataForDate(period.get('date'), city)
    elif period.get('date-period') != None:
        return queryDateForDateRange(period.get('date-period'), city)
    else:
        return 'does not exist in the database'
                                     
def queryDateForDateRange(datePeriod, city):
    print("Inside Query for Date Period")
    startDate = datePeriod.split('/')[0]
    print ("The start date is:" + startDate)
    endDate = datePeriod.split('/')[1]
    print ("The end date is:" + endDate)
    startAmount = None
    amount = 0
    sale = mongo.db.sales  
    
    try: 
        for s in sale.find({'city': city}):
            print ("The date is:" + s['date'])
            if (dt.strptime(s['date'], "%Y-%m-%d") >= dt.strptime(startDate, "%Y-%m-%d")) and (dt.strptime(s['date'], "%Y-%m-%d") <= dt.strptime(endDate, "%Y-%m-%d")):
                print ("Inside if")
                startAmount = 0
                amount = amount + int(s['amount'])
        if startAmount != None:
            return str(amount)
        else:
            return 'not there in the database'
    except Exception:
        print("Could not query database")
        return ''
    

def queryDataForDate(date, city):
    print("Inside Query for Date")
    sale = mongo.db.sales
    startAmount = None
    amount = 0
    
    try: 
        for s in sale.find({'city': city,'date': date}):
            print("The sales amount is:"+s['amount'])
            startAmount = 0
            amount = amount + int(s['amount'])
        if startAmount != None:
            return str(amount)
        else:
            return 'not there in the database'
    except Exception:
        print("Could not query database")
        return ''


# Sending a message back through Messenger.
def send_message(sender_id, message_text):
    print('in send msg')
    r = requests.post("https://api.api.ai/v1/",
 
        
 
        headers={"Content-Type": "application/json"},
 
        data=json.dumps({
        "recipient": {"id": sender_id},
        "message": {"text": message_text}
    }))



# Takes a string of natural language text, passes it to ApiAI, returns a
# response generated by an ApiAI bot.
def parse_natural_text(user_text):
    print('hi there!')
    # Sending a text query to our bot with text sent by the user.
    request = ai.text_request()
    request.query = user_text
 
    # Receiving the response.
    response = json.loads(request.getresponse().read().decode('utf-8'))
    responseStatus = response['status']['code']
    if (responseStatus == 200):
        # Sending the textual response of the bot.
        return (response['result']['fulfillment']['speech'])
 
    else:
        return ("Sorry, I couldn't understand that question")
 
    # NOTE:
    # At the moment, all messages sent to ApiAI cannot be differentiated,
    # they are processed as a single conversation regardless of concurrent
    # conversations. We need to perhaps peg a session id (ApiAI) to a recipient
    # id (Messenger) to fix this.
 
    # request.session_id = "<SESSION ID, UNIQUE FOR EACH USER>"
 
# Sends the message in segments delimited by a period.
def send_message_staggered(sender_id, message_text):
    print('staggered') 
    sentenceDelimiter = ". "
    messages = message_text.split(sentenceDelimiter)
   
    for message in messages:
        send_message(sender_id, message)

@app.route('/add')

def add():
    
    sale = mongo.db.sales
    sale.insert({'city' : 'Mumbai', 'date': 'June', 'amount' : '1900'})
    return 'Added Sales row'

@app.route('/query')
def query():
    sale = mongo.db.sales
    output = []
    for s in sale.find({'city': 'Pune'}):
        output.append({'city' : s['city'], 'date' : s['date'], 'amount': s['amount']})
    return jsonify({'output':output})

if __name__ == "__main__":
    app.run()
    '''app.run(debug = True, port = 80)'''
    
'''
End of file!!!!
'''
