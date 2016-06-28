

.PHONY: deploy test clean lint

deploy: clean package upload

clean:
	rm -rf hslbot.zip

package:
	zip -r hslbot.zip departures.py lambdamain.py requests pytz

upload:
	aws lambda update-function-code --function-name $(LAMBDANAME) --zip-file fileb://hslbot.zip --region us-east-1

lint:
	pylint departures.py lambdamain.py 2>/dev/null; true

test:
	python -m unittest discover test