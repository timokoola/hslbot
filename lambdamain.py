"""Lambda handle function for Alexa skill"""
from __future__ import print_function
import departures
from departures import city_code, normalize_stopcode
from alexarequests import launch_response, response_creator, DynamoStorage
from keys import bot_gid, hsl_username, hsl_passcode


def lambda_handler(event, context):
    """Lambda handle function for Alexa skill"""
    hsl = departures.HslRequests(hsl_username,
                                 hsl_passcode)

    if event["session"]["application"]["applicationId"] != bot_gid:
        return {"errorMessage": "Bad request"}

    if event.has_key("request"):
        # card = event["request"]["type"]
        event_type = event["request"].get("type", "LaunchRequest")
        if event_type == "LaunchRequest":
            return launch_response()
        elif event_type == "IntentRequest":
            intent_ = event["request"]["intent"]
            intentname = intent_["name"]
            if intentname == "GetAirportTrains":
                stop_param = "V0531"
            elif intentname == "GetStopInfo":
                slots = intent_["slots"]
                stop = normalize_stopcode(slots["Stop"].get("value", "1000"))
                city = slots["City"].get("value", "")
                stop_param = city_code(city) + stop
            elif intentname == "AMAZON.HelpIntent":
                return launch_response()
            elif intentname == "AMAZON.RepeatIntent":
                store = DynamoStorage(event)
                stop_param = store.get_home_stop()
                if stop_param:
                    pass
                else:
                    return launch_response()

    text, card, _ = hsl.relative_time(stop_param)

    return response_creator(text, card)

# reprompt": {
#       "outputSpeech": {
#         "type": "PlainText",
#         "text": "Can I help you with anything else?"
#       }
#     },
