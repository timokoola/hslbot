def launch_response():
    text_item = {"type": "PlainText",
                 "text": "Welcome to Helsinki buses. " +
                         "We can tell you departures on Helsinki area " +
                         "bus stops." +
                         "Just utter the four digit stop code for" +
                         " next departures. " +
                         "Try for example: Helsinki 1001. " +
                         "Ask to repeat for updates on same stop"}
    card_item = {"type": "Simple", "title": "Helsinki bus stops",
                 "content": "Helsinki bus stops can tell you next departures on" +
                            " any Helsinki metropolitan area bus stop."}
    reprompt = {
        "outputSpeech": {"text": "Which stop do you want to know about?",
                         "type": "PlainText"}}
    response = {"version": "1.0",
                "response": {"outputSpeech": text_item, "card": card_item},
                "shouldEndSession": False}

    return response


def response_creator(text, card):
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
    def __init__(self, request):
        self.request_json = json.loads(request)
        self.dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
        self.table = self.dynamodb.Table("HslBotUsers")

    def get_user_id(self):
        return self.request_json["session"]["user"]["userId"]

    def write_previous_stop(self, stop_code):
        try:
            userId = self.get_user_id()
        except KeyError:
            return
        response = self.table.query(
            KeyConditionExpression=Key('userkey').eq(self.get_user_id()))
        count = response.get("Count", 0)
        if count > 0:
            cresp = self.table.put_item(
                Item={"userkey": "test1", "stopcode": stop_code})
        else:
            cresp = self.table.update_item(Key={"userkey": "test1"},
                                           UpdateExpression="set stopcode = :s",
                                           ExpressionAttributeValues={
                                               ':s': stop_code},
                                           ReturnValues="UPDATED_NEW")

    def get_home_stop(self):
        try:
            userId = self.get_user_id()
        except KeyError:
            return
        response = self.table.query(
            KeyConditionExpression=Key('userkey').eq(self.get_user_id()))
        try:
            return response.get('Items')[0]["stopcode"]
        except KeyError:
            return None
