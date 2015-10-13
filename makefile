BRANCH=$(shell bash .getbranch)

show:
	@echo "Branch: $(BRANCH)"

start:	
	@echo "Starting process..."
	@nohup ./tquakesd > log/tquakes.out 2>&1 &

stop:
	@echo "Stopping process..."
	@skill -9 tquakesd

install:
	@echo "Installing tQuakes..."
	@bash install.sh

permissions:
	@echo "Setting permissions for web..."
	@chown -R www-data.www-data .

clean:
	@echo "Cleaning..."
	@find . -name "*~" -exec rm {} \;
	@find . -name "*.pyc" -exec rm {} \;
	@find . -name "#*#" -exec rm {} \;
	@touch scratch/remove
	@rm scratch/*

cleandata:clean
	@echo "Cleaning data..."
	@touch data/quakes/ooooooo
	@rm -r data/quakes/???????

watch:
	@watch -d -n 2 bash tquakes-status.sh

unlock:
	@echo "Unlocking all quakes..."
	@find data/quakes -name ".lock" -exec rm {} \;

backup:
	@echo "Backuping Quakes data..."
	@mysqldump -u root -p tQuakes Quakes > data/sql/Quakes.sql

backupall:
	@echo "Backuping tQuakes database..."
	@mysqldump -u root -p tQuakes > data/sql/tQuakes.sql

gitconfig:
	@echo "Configuring git user..."
	@git config --global user.email "seapudea@gmail.com"
	@git config --global user.name "SEAP UdeA"

commit:
	@echo "Commiting changes..."
	@git commit -am "Commit"
	@git push origin $(BRANCH)

pull:
	@echo "Pulling from repository..."
	@git reset --hard HEAD	
	@git pull origin $(BRANCH)
