import requests
import json
import tweepy
import os

def lambda_handler(event, context):
    
    if (event['session']['application']['applicationId'] != os.environ['appID']):
        raise ValueError("Invalid Application ID")
    
    if (event['session']['user']['userId'] != os.environ['userID']):
        raise ValueError("Invalid user ID")
    
    if event["request"]["type"] == "LaunchRequest":
        return on_launch(event["request"], event["session"])
    elif event["request"]["type"] == "IntentRequest":
        return on_intent(event["request"], event["session"])
    elif event["request"]["type"] == "SessionEndedRequest":
        return on_session_ended(event["request"], event["session"])
        
def on_intent(intent_request, session):
    
    intent = intent_request["intent"]
    intent_name = intent_request["intent"]["name"]
    
    if intent_name == "listColours":
        return get_colours()
    elif intent_name == "currentColour":
        return get_currentColour()
    elif intent_name == "changeColour":
        return set_colour(intent)
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
    speech_output += requests.get("http://api.thingspeak.com/channels/1417/field/1/last.txt").text
    reprompt_text = ""
    should_end_session = True
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session)) 

def set_colour(intent):
    targetcolour=intent["slots"]["Colour"]["value"]
    auth = tweepy.OAuthHandler(os.environ['consumer_key'], os.environ['consumer_secret'])
    auth.set_access_token(os.environ['access_token'], os.environ['access_secret'])

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



