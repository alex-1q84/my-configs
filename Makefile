VENV = venv
DEPENDENCY = requirements.txt

init: $(DEPENDENCY)
	-echo "init complete"

$(VENV):
	python3 -m venv $(VENV)

$(DEPENDENCY): $(VENV)
	$(VENV)/bin/python3 -m pip install -r requirements.txt

clean:
	rm -rf $(VENV)

.PHONY: clean init
