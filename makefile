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
	@find . -name "*.png" -exec rm {} \;

cleanscratch:
	@touch scratch/remove
	@rm -r scratch/*

cleandata:
	@echo "Cleaning data..."
	@touch data/quakes/ooooooo
	@rm -r data/quakes/???????
	@touch ~tquakes/tQuakes/foo
	@rm ~tquakes/tQuakes/*

cleanall:cleandata cleanscratch clean

watch:
	@watch -d -n 2 bash tquakes-status.sh

unlock:
	@echo "Unlocking all quakes..."
	@find data/quakes -name ".lock" -exec rm {} \;

backup:
	@echo "Backuping Quakes data..."
	@bash tquakes-backup.sh Quakes

backupall:
	@echo "Backuping tQuakes database..."
	@bash tquakes-backup.sh tQuakes

restore:
	@echo "Restoring table Quakes..."
	@cat data/sql/dump/Quakes.sql.7z-* > data/sql/Quakes.sql.7z
	@p7zip -d data/sql/Quakes.sql.7z
	@echo "Enter root mysql password..."
	@mysql -u root -p tQuakes < data/sql/Quakes.sql
	@p7zip data/sql/Quakes.sql

restoreall:
	@echo "Restoring database..."
	@cat data/sql/dump/tQuakes.sql.7z-* > data/sql/tQuakes.sql.7z
	@p7zip -d data/sql/tQuakes.sql.7z
	@echo "Enter root mysql password..."
	@mysql -u root -p tQuakes < data/sql/tQuakes.sql
	@p7zip data/sql/tQuakes.sql

installkeys:
	@echo "Installing new station keys..."
	@bash tquakes-keys.sh

gitconfig:
	@echo "Configuring git user..."
	@git config --global user.email "seapudea@gmail.com"
	@git config --global user.name "SEAP UdeA"

commit:
	@echo "Commiting changes..."
	@touch .htaccess
	@-git commit -am "Commit"
	@git push origin $(BRANCH)

pull:
	@echo "Pulling from repository..."
	@git reset --hard HEAD	
	@git pull origin $(BRANCH)

station:
	@echo "Changing to station branch..."
	@git checkout station

resetquakes:
	@echo "Resetting quakes..."
	@mysql -u root -p tQuakes -e "update Quakes set astatus='0',stationid='',adatetime='',qsignal='',qphases='';"

plotdata:
	@echo "Generating website plots..."
	@bash tquakes-plots.sh
