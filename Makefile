.PHONY: train pipeline roi test dev-check

train: dev-check
	bash daily_train.sh

pipeline: dev-check
	bash run_pipeline_with_venv.sh

roi: dev-check
	bash run_roi_pipeline.sh

test: dev-check
	.venv/bin/pytest -q

dev-check:
    bash utils/dev-check.sh
