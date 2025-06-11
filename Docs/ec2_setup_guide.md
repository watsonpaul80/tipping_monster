# EC2 Setup Guide

This guide summarises the steps to run Tipping Monster on an AWS EC2 instance.

## Dev Mode and Telegram

Set `TM_DEV_MODE=1` or use the `--dev` flag with CLI scripts to avoid sending
real Telegram posts during tests. Messages are logged to `logs/dev/telegram.log`
instead.

