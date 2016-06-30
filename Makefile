

.PHONY: deploy test clean lint

deploy: clean package staging-upload upload

staging: clean package staging-upload integrationtest

clean:
	rm -rf hslbot.zip

package:
	zip -r hslbot.zip departures.py lambdamain.py requests pytz

upload:
	aws lambda update-function-code --function-name $(LAMBDANAME) --zip-file fileb://hslbot.zip --region us-east-1

staging-upload:
	aws lambda update-function-code --function-name hslstop --zip-file fileb://hslbot.zip --region eu-west-1

lint:
	pylint departures.py lambdamain.py 2>/dev/null; true

unittest:
	python -m unittest test.testdepartures

integrationtest:
	python -m unittest test.stagingtests
