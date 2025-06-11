.PHONY: train pipeline roi test dev-check

train: dev-check
        bash core/daily_train.sh

pipeline: dev-check
        bash core/run_pipeline_with_venv.sh

roi: dev-check
        bash roi/run_roi_pipeline.sh

test: dev-check
	.venv/bin/pytest -q
dev-check:
	bash utils/dev-check.sh

