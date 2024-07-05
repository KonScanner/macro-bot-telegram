ruff_call:
	ruff check --select I --fix .
	ruff format .

format: ruff_call

sync:
	uv pip sync requirements.txt