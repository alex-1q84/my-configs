VENV = venv
DEPENDENCY = requirements.txt

backup: init
	venv/bin/python3 my_configs.py

init: $(DEPENDENCY)
	@echo "init complete"

$(VENV):
	uv venv $(VENV)

$(DEPENDENCY): $(VENV)
	uv pip install -r requirements.txt

clean:
	rm -rf $(VENV)

.PHONY: link clean init
