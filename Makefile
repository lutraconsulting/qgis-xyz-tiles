#### Functions and commands

# Recursive file search function
rwildcard=$(foreach d,$(wildcard $1*),$(call rwildcard,$d/,$2) $(filter $(subst *,%,$2),$d))

# Platform commands
ifeq ($(OS),Windows_NT)
	# Set paths to call pylupdate5 correctly
	PATH := /osgeo4w/apps/Qt5/bin:$(PATH)
	ifneq ($(wildcard /osgeo4w/apps/Python37),)
		PYTHONHOME := /osgeo4w/apps/Python37
	else ifneq ($(wildcard /osgeo4w/apps/Python36),)
		PYTHONHOME := /osgeo4w/apps/Python36
	else
		ERROR = Neither Python37 nor Python36 were found in the OSGeo4W root!
	endif
	# Set pylupdate5 command
	pylupdate5 = cmd //c python3 -m PyQt5.pylupdate_main
else
	pylupdate5 = pylupdate5
endif


#### Configuration

# Plugin name
PLUGINNAME	= tiles_xyz

# List ts and qm files
TS_FILES	= $(call rwildcard,,*.ts)
QM_FILES	= $(patsubst %.ts,%.qm,$(TS_FILES))

# List py files
PY_FILES	= $(call rwildcard,,*.py)

# List images
PNG_FILES	= $(call rwildcard,,*.png)

# Install files
INSTALL_FILES = \
	$(PY_FILES) \
	$(QM_FILES) \
	$(PNG_FILES) \
	tiles_xyz/metadata.txt


#### Targets

default: qm

.PHONY: help
help:
	@echo
	@echo "------------------------------"
	@echo "        Build targets"
	@echo "------------------------------"
	@echo qm
	@echo update_ts
	@echo update_ts_clean
	@echo package
	@echo clean

check_error:
ifdef ERROR
	$(error $(ERROR))
endif

$(QM_FILES): %.qm : %.ts
	@echo "qm: $@"
	@lrelease -silent $<

qm: $(QM_FILES)

$(TS_FILES): check_error
	@echo "ts: $@"
	@$(pylupdate5) $(PY_FILES) -ts $@

update_ts: check_error
	@echo
	@echo "------------------------------"
	@echo "    Updating translations"
	@echo "------------------------------"
	@$(foreach var,$(LOCALES),echo $(var); $(pylupdate5) $(PY_FILES) -ts $(TS_FILES);)
	@echo done!

update_ts_clean: check_error
	@echo
	@echo "------------------------------"
	@echo "Removing obsolete translations"
	@echo "------------------------------"
	@$(foreach var,$(LOCALES),echo $(var); $(pylupdate5) $(PY_FILES) -ts $(TS_FILES) -noobsolete;)
	@echo done!

package: $(INSTALL_FILES)
	@echo
	@echo "------------------------------"
	@echo "      Preparing package"
	@echo "------------------------------"
	@mkdir -p dist
	@rm -fv $(wildcard dist/$(PLUGINNAME)*.zip)
	@$(eval ARCHIVE := $(PLUGINNAME)_$(strip $(shell awk -F = '/version/ {print $$2}' tiles_xyz/metadata.txt)).zip)
	@echo Adding files to $(ARCHIVE):
	@zip dist/$(ARCHIVE) $(INSTALL_FILES)
	@echo done!

.PHONY : clean
clean:
	@echo
	@echo "------------------------------"
	@echo "           Cleaning"
	@echo "------------------------------"
	@rm -fv $(QM_FILES)
	@rm -fvr dist
	@echo done!
