VENV = venv
DEPENDENCY = requirements.txt

backup: init
	venv/bin/python3 my_configs.py

init: $(DEPENDENCY)
	@echo "init complete"

$(VENV):
	python3 -m venv $(VENV)

$(DEPENDENCY): $(VENV)
	$(VENV)/bin/python3 -m pip install -r requirements.txt

clean:
	rm -rf $(VENV)

.PHONY: link clean init
