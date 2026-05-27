# ContentPilot Cron Setup

## Install

```bash
# Replace REPO_ROOT in the crontab file with your actual path, then:
crontab infra/cron/crontabs/contentpilot

# Verify
crontab -l
```

## How jobs run

All jobs go through `scripts/run_job.sh`:

```
cron → run_job.sh <module> → docker compose run --rm <module> python main.py
```

## Logs

- Per-module: `data/runtime/<module>.log`
- Cron-level:  `data/runtime/cron.log`
- Rotate automatically at 5MB

## Adding a new module

1. Create `modules/<name>/main.py` with `managed_run("<name>")`
2. Add a service block in `docker-compose.yml`
3. Add a cron line here

No other changes needed.
