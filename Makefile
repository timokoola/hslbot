

.PHONY: deploy unittest integrationtest clean lint

deploy: clean package staging-upload upload

telegramdeploy: clean telegrampackage telegramupload

facebookdeploy: clean facebookpackage messengerupload

staging: clean package staging-upload integrationtest

clean:
	rm -rf hslbot.zip rm -rf telegrambot.zip -rf messengerbot.zip

package:
	zip -r hslbot.zip departures.py lambdamain.py alexarequests.py keys.py requests pytz

telegrampackage:
	zip -r telegrambot.zip departures.py telegramlambda.py keys.py requests telepot urllib3 pytz

facebookpackage:
	zip -r messengerbot.zip departures.py messengerlambda.py keys.py pymessenger pytz requests urllib3 six requests_toolbelt

upload:
	aws lambda update-function-code --function-name $(LAMBDANAME) --zip-file fileb://hslbot.zip --region us-east-1

messengerupload:
	aws lambda update-function-code --function-name hslmessengerbot --zip-file fileb://messengerbot.zip --region us-east-1

staging-upload:
	aws lambda update-function-code --function-name hslstop --zip-file fileb://hslbot.zip --region eu-west-1

telegramupload:
	aws lambda update-function-code --function-name telegramlambda --zip-file fileb://telegrambot.zip --region eu-west-1

telegramsetwebhook:
	python telegramsetup.py

lint:
	pylint departures.py lambdamain.py alexarequests.py 2>/dev/null; true

unittest:
	python -m unittest test.testdepartures

integrationtest:
	python -m unittest test.stagingtests
