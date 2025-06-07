# Model Storage

The repository no longer contains the trained XGBoost model binaries. Each model
is saved as a tarball and uploaded to the `tipping-monster` S3 bucket under the
`models/` prefix during training.

To fetch the latest model manually:

```bash
aws s3 cp s3://tipping-monster/models/<model-tarball> .
# example: aws s3 cp s3://tipping-monster/models/tipping-monster-xgb-model-2025-06-06.tar.gz .
```

Extract the archive to obtain `tipping-monster-xgb-model.bst` and
`features.json`:

```bash
tar -xzf tipping-monster-xgb-model-2025-06-06.tar.gz
```

The inference script `run_inference_and_select_top1.py` automatically selects
the most recent `tipping-monster-xgb-model-*.tar.gz` in the repository root. If
no tarball is found, it exits with `FileNotFoundError: No model tarball found.
Download one from S3 or run training.` When a path or S3 key is provided via
`--model`, the script downloads that file if missing locally.

Large model files are tracked with **Git LFS**. If you clone the repository with
LFS enabled, running `git lfs pull` will download any referenced model pointers.
