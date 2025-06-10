# Developer Command Reference

This page lists common commands useful when working on Tipping Monster.

## Environment Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # fill in credentials
```

## Checking Your Setup

```bash
./utils/dev-check.sh  # verifies Python version and environment variables
pre-commit run --files $(git ls-files '*.py')  # linting
```

## Running Tests

```bash
make test
```

## Running the Pipeline

```bash
make pipeline           # full daily pipeline
make roi                # generate ROI reports
make train              # train a new model
```

Each make target wraps the underlying scripts in `core/` and `roi/`.
Use `make pipeline -- --dev` to disable S3 uploads and Telegram posts during development.

## Useful CLI Examples

```bash
python cli/tmcli.py healthcheck --date YYYY-MM-DD
python cli/tmcli.py dispatch-tips YYYY-MM-DD --telegram
python cli/tmcli.py send-roi --date YYYY-MM-DD --telegram
```

The `--telegram` flag sends output to the configured chat. Omit it to print to the console.

## Inference Standalone

Run the inference step from the repository root:

```bash
python core/run_inference_and_select_top1.py --dev
```

Use `--dev` to skip the S3 upload.
Running the command inside `core/` without `PYTHONPATH=..` will fail.
