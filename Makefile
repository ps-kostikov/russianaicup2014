package:
	python make.py

clean:
	find -name \*.pyc -exec rm {} \;
	rm strategy.zip