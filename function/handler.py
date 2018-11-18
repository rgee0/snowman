import urllib2
import json
import tweepy

def handle(req):

    event = json.loads(req)
    with open("/var/openfaas/secrets/skill","r") as skill:
        skill_id = skill.read().strip()
    
    if (event['session']['application']['applicationId'] != skill_id):
        raise ValueError("Invalid Application ID")

    with open("/var/openfaas/secrets/userid","r") as userid:
        user_id = userid.read().strip()
    
    if (event['session']['user']['userId'] != user_id ):
        raise ValueError("Invalid user ID")
    
    if event["request"]["type"] == "LaunchRequest":
        retVal=on_launch(event["request"], event["session"])
    elif event["request"]["type"] == "IntentRequest":
        retVal=on_intent(event["request"], event["session"])
    elif event["request"]["type"] == "SessionEndedRequest":
        retval=on_session_ended(event["request"], event["session"])
         
    print json.dumps(retVal)

def on_intent(intent_request, session):
    
    intent = intent_request["intent"]
    intent_name = intent_request["intent"]["name"]
    
    if intent_name == "listColours":
        return get_colours()
    elif intent_name == "currentColour":
        return get_currentColour()
    elif intent_name == "changeColour":
        return set_colour(intent)
    elif intent_name == "whereabouts":
	return get_whereabouts()
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")

def get_colours():
    session_attributes = {}
    card_title = "Snowman"
    speech_output = "Thank you for asking snowman about available colours. " \
                    "You can choose from red, green, blue, cyan, white, warmwhite, " \
                    "purple, magenta, yellow, orange or pink."
    reprompt_text = ""
    should_end_session = True
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_currentColour():
    session_attributes = {}
    card_title = "Snowman"
    speech_output = "The snowman tells me that he is currently displaying "
    speech_output = speech_output + urllib2.urlopen("http://api.thingspeak.com/channels/1417/field/1/last.txt").read()
    reprompt_text = ""
    should_end_session = True
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session)) 

def get_whereabouts():
    session_attributes = {}
    card_title = "Snowman"
    speech_output = "The snowman says he was running through AWS Lambda but now prefers to run on OpenFaz - Serverless Functions Made Simple."
    reprompt_text = ""
    should_end_session = True
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def set_colour(intent):
    targetcolour=intent["slots"]["Colour"]["value"]

    with open("/var/openfaas/secrets/consumerKey","r") as consumerkey:
        consumer_key = consumerkey.read().strip()
    with open("/var/openfaas/secrets/consumerSecret","r") as consumersecret:
        consumer_secret = consumersecret.read().strip()

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)

    with open("/var/openfaas/secrets/accessToken","r") as accesstoken:
        access_token = accesstoken.read().strip()
    with open("/var/openfaas/secrets/accessSecret","r") as accesssecret:
        access_secret = accesssecret.read().strip()

    auth.set_access_token(access_token, access_secret)

    tweet = "#cheerlights " + targetcolour
    status = tweepy.API(auth).update_status(status=tweet)
    
    session_attributes = {}
    card_title = "Snowman"
    speech_output = "OK, I'll ask the snowman to display " + targetcolour
    reprompt_text = ""
    should_end_session = True
    
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        "outputSpeech": {
            "type": "PlainText",
            "text": output
        },
        "card": {
            "type": "Simple",
            "title": title,
            "content": output
        },
        "reprompt": {
            "outputSpeech": {
                "type": "PlainText",
                "text": reprompt_text
            }
        },
        "shouldEndSession": should_end_session
    }

def build_response(session_attributes, speechlet_response):
    return {
        "version": "1.0",
        "sessionAttributes": session_attributes,
        "response": speechlet_response
    }
