"""AWS or Alexa related helper functions"""
import boto3
from boto3.dynamodb.conditions import Key


def launch_response():
    """Response when no specific stop is defined"""
    text_item = {"type": "PlainText",
                 "text": "Welcome to Helsinki buses. " +
                         "We can tell you departures on Helsinki area " +
                         "bus stops." +
                         "Just utter the four digit stop code for" +
                         "next departures. " +
                         "Try for example: Helsinki 1001. " +
                         "Ask to repeat for updates on same stop"}
    card_item = {"type": "Simple", "title": "Helsinki bus stops",
                 "content": "Helsinki bus stops can tell you next departures on" +
                            " any Helsinki metropolitan area bus stop."}
    response = {"version": "1.0",
                "response": {"outputSpeech": text_item, "card": card_item},
                "shouldEndSession": False}

    return response


def response_creator(text, card):
    """
    Builds a response with speech part and Alexa appcard contents
    :param text: text to be spoken
    :param card: text for the app card
    :return: JSON object to be returned
    """
    text_item = {"type": "PlainText", "text": text}
    card_item = {"type": "Simple", "title": "Stop Info", "content": card}
    reprompt = {
        "outputSpeech": {"text": "Which stop do you want to know about?",
                         "type": "PlainText"}}
    response = {"version": "1.0",
                "response": {"outputSpeech": text_item, "card": card_item,
                             "reprompt": reprompt,
                             "shouldEndSession": True}}

    return response


class DynamoStorage(object):
    """Simple wrapper object to hide DynamoDB details"""

    def __init__(self, request):
        """
        Constructs DynamoDB objects for accessing the DB
        :param request: original request, used for scanning the username
        """
        self.request_json = request
        self.dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
        self.table = self.dynamodb.Table("HslBotUsers")

    def get_user_id(self):
        """
        Returns the user id of the well formed request
        :return: Amazon username of the user who requested information
        """
        return self.request_json["session"]["user"]["userId"]

    def write_previous_stop(self, stop_code):
        """
        Stores the stop to dynamo db for further requests
        :param stop_code: stop code to store
        """
        try:
            user_id = self.get_user_id()
        except KeyError:
            return
        response = self.table.query(
            KeyConditionExpression=Key('userkey').eq(self.get_user_id()))
        count = response.get("Count", 0)
        username = user_id
        if count > 0:
            self.table.put_item(
                Item={"userkey": username, "stopcode": stop_code})
        else:
            self.table.update_item(Key={"userkey": username},
                                   UpdateExpression="set stopcode = :s",
                                   ExpressionAttributeValues={
                                       ':s': stop_code},
                                   ReturnValues="UPDATED_NEW")

    def get_home_stop(self):
        """
        Gets the code for the stored stop from Dynamo DB
        :return: stop code
        """
        try:
            self.get_user_id()
        except KeyError:
            return
        response = self.table.query(
            KeyConditionExpression=Key('userkey').eq(self.get_user_id()))
        try:
            return response.get('Items')[0]["stopcode"]
        except KeyError:
            return None
