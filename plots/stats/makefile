BRANCH=$(shell bash .getbranch)
NEWSCRIPT=""

all:
	@for script in *.py;do python $$script;done

clean:
	@echo "Cleaning..."
	@find . -name "*~" -exec rm {} \;
	@find . -name "*.pyc" -exec rm {} \;
	@find . -name "#*#" -exec rm {} \;
	@find . -name "*.png" -exec rm {} \;
	@for dir in *.history;do touch $$dir/delete;done
	@-rm *.history/*

new:
	@echo "Creating new script '$(NEWSCRIPT)'..."
	@test $(NEWSCRIPT) != ""
	@cp template.tpy $(NEWSCRIPT).py
	@cp template.tconf $(NEWSCRIPT).conf
	@mkdir $(NEWSCRIPT).history
	@touch $(NEWSCRIPT).history/.dir
	@git add $(NEWSCRIPT).*
	@git add $(NEWSCRIPT).history/.dir
