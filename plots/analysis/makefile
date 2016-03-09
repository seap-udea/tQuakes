BRANCH=$(shell bash .getbranch)

new:
	@echo "Creating new script '$(NEWSCRIPT)'..."
	@test $(NEWSCRIPT) != ""
	@cp template.tpy $(NEWSCRIPT).py
	@cp template.tconf $(NEWSCRIPT).conf
	@cp template.thtml $(NEWSCRIPT).html
	@mkdir $(NEWSCRIPT).history
	@touch $(NEWSCRIPT).history/.dir
	@echo "*" > $(NEWSCRIPT).history/.gitignore
	@git add -f $(NEWSCRIPT).*
	@git add -f $(NEWSCRIPT).history/.dir
	@git add -f $(NEWSCRIPT).history/.gitignore

all:
	@for script in *.py;do python $$script;done
	@make permissions

repeat:
	@test $(SCRIPT) != ""
	@for conf in $(shell find . -name "$(SCRIPT)__*.conf");do python $(SCRIPT).py $$conf;done

clean:
	@echo "Cleaning..."
	@find . -name "*~" -exec rm {} \;
	@find . -name "*.pyc" -exec rm {} \;
	@find . -name "#*#" -exec rm {} \;
	@find . -name "*.png" -exec rm {} \;
	@for dir in *.history;do touch $$dir/delete;done
	@-rm *.history/*

permissions:
	@echo "Setting permissions for web..."
	@chown -R www-data.www-data .
