import unittest

import requests

unauth_json = {
    "session": {
        "sessionId": "mockSessioId",
        "application": {
            "applicationId": "mockappid"
        },
        "attributes": {},
        "user": {
            "userId": ""
        },
        "new": True
    },
    "request": {
        "type": "IntentRequest",
        "requestId": "EdwRequestId.5cce52dd-d824-4055-a3d7-797e42076a2e",
        "timestamp": "2016-06-29T19:34:56Z",
        "intent": {
            "name": "GetAirportTrains",
            "slots": {}
        },
        "locale": "en-US"
    },
    "version": "1.0"
}


class StagingTests(unittest.TestCase):
    """Tests run after staging deployment sending JSON objects to lambda
    function in staging environment in West Europe (production is in
    North america as per Alexa requirements"""

    def setUp(self):
        """Set up, read test url from non git keys file"""
        f = open("keys.keys")
        lines = f.readlines()
        f.close()
        self.appid = lines[3].strip()
        self.stagingurl = lines[4].strip()

    def test_400(self):
        r = requests.post(self.stagingurl, json=unauth_json)
        self.assertTrue(r.status_code == 400)
