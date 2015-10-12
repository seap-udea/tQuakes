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

cleandata:
	@echo "Cleaning data..."
	@rm -r data/quakes/???????

unlock:
	@echo "Unlocking all quakes..."
	@find data/quakes -name ".lock" -exec rm {} \;

gitconfig:
	@echo "Configuring git user..."
	@git config --global user.email "seapudea@gmail.com"
	@git config --global user.name "SEAP UdeA"

commit:
	@echo "Commiting changes..."
	@git commit -am "Commit"
	@git push origin master

pull:
	@echo "Pulling from repository..."
	@git reset --hard HEAD	
	@git pull
	@chown -R www-data.www-data .
