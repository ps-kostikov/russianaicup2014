package:
	python make.py

best_with_quick:
	SCRIPTDIR=`pwd`
	java -cp ".:*:$$SCRIPTDIR/*" -jar "local-runner.jar" properties/render_local_quick.properties &
	sleep 1
	PYTHONPATH=strategies/best:src:. python Runner.py

best_with_weak_willed:
	SCRIPTDIR=`pwd`
	java -cp ".:*:$$SCRIPTDIR/*" -jar "local-runner.jar" properties/render_local_local.properties &
	sleep 1
	PYTHONPATH=strategies/best:src:. python Runner.py 127.0.0.1 31001 0000000000000000 &
	sleep 1
	PYTHONPATH=strategies/weak-willed:src:. python Runner.py 127.0.0.1 31002 0000000000000000

clean:
	find -name \*.pyc -exec rm {} \;
	rm -f strategy.zip
	rm -f result.txt