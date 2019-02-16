
BRANCH=$(shell bash .getbranch)

key:
	eval $(keychain --eval id_rsa_seap)

show:
	@echo "Branch: $(BRANCH)"

start:cleandata
	@echo "Starting process..."
	@touch stop
	@rm stop
	@nohup ./tquakesd > log/tquakes.out 2>&1 &

stop:
	@echo "Stopping process..."
	@skill -9 tquakesd
	@sudo pkill python
	@touch stop
	@rm .start &> /dev/null

status:
	@echo "Checking status..."
	@bash tquakes-status.sh

install:
	@echo "Installing tQuakes..."
	@bash install.sh

clean:
	@echo "Cleaning..."
	@find . -name "*~" -exec rm {} \;
	@find . -name "*.pyc" -exec rm {} \;
	@find . -name "#*#" -exec rm {} \;
	@touch scratch/remove
	@rm scratch/*

cleandata:
	@echo "Cleaning calculations..."
	@touch data/quakes/ooooooo
	@rm -r data/quakes/???????

cleanall:clean cleandata
	@-rm log/*

unlock:
	@echo "Unlocking all quakes..."
	@find data/quakes -name ".lock" -exec rm {} \;

gitconfig:
	@echo "Configuring git user..."
	@git config --global user.email "seapudea@gmail.com"
	@git config --global user.name "SEAP UdeA"

commit:
	@echo "Commiting changes..."
	@-git commit -am "Commit"
	@git push origin $(BRANCH)

pull:
	@echo "Pulling from repository..."
	@git reset --hard HEAD	
	@git pull origin $(BRANCH)

master:
	@echo "Changing to master branch..."
	@git checkout master

resetquakes:
	@echo "Resetting all quakes to original state..."
	@find data/quakes/??????? -type f -name ".[a-zA-Z]*" -exec rm {} \;
	@find data/quakes -maxdepth 1 -type d -not -name TEMPLATE -not -name quakes -exec touch {}/.fetch \;

fetch:
	python tquakes-fetch.py

prepare:
	python tquakes-prepare.py

run:
	python tquakes-run.py

analysis:
	python tquakes-analysis.py

submit:
	python tquakes-submit.py

parallel:
	bash tquakes-parallel.sh

pipeline:fetch prepare run analysis submit
