package:
	python make.py

local_with_quick:
	SCRIPTDIR=`pwd`
	java -cp ".:*:$$SCRIPTDIR/*" -jar "local-runner.jar" properties/render_local_quick.properties &
	sleep 2
	PYTHONPATH=strategies/$(PLAYER1):src:. python Runner.py

local_with_local:
	SCRIPTDIR=`pwd`
	java -cp ".:*:$$SCRIPTDIR/*" -jar "local-runner.jar" properties/render_local_local.properties &
	sleep 2
	PYTHONPATH=strategies/$(PLAYER1):src:. python Runner.py 127.0.0.1 31001 0000000000000000 &
	sleep 2
	PYTHONPATH=strategies/$(PLAYER2):src:. python Runner.py 127.0.0.1 31002 0000000000000000

repeat:
	PYTHONPATH=strategies/$(PLAYER1):src:. python Runner.py

plugins:
	javac -encoding UTF-8 plugins/*.java -cp plugins

test:
	PYTHONPATH=src:. python tests/test_geometry.py
	PYTHONPATH=src:. python tests/test_algorithm.py

clean:
	find -name \*.pyc -exec rm {} \;
	rm -f strategy.zip
	rm -f result.txt

.PHONY: plugins