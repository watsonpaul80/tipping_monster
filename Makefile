.PHONY: train pipeline roi test dev-check

train: dev-check
	. .venv/bin/activate && bash core/daily_train.sh

pipeline: dev-check
	. .venv/bin/activate && bash core/run_pipeline_with_venv.sh

roi: dev-check
	. .venv/bin/activate && bash roi/run_roi_pipeline.sh

test: dev-check
	.venv/bin/pytest -q

dev-check:
	. .venv/bin/activate && bash utils/dev-check.sh