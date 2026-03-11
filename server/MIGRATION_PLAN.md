TrendForge V9 Migration Plan
Important:
Do NOT delete your current root-level working files yet.
Phase 1:
Create folders:
pipeline
sources
engines
push
sql
docs
legacy_root
Phase 2:
Copy current working files into new folders.
Copy first, do not move first.
Phase 3:
Use run_v9_pipeline.sh to test the modular layout.
Phase 4:
Validate:
SQL migration runs
source scripts run
build_trends_from_raw.py runs
expansion works
MJ prompt works
push engine logs to push_log
Feishu sends or cooldown skip is visible
Phase 5:
Only after validation, update systemd to point to pipeline/run_v9_pipeline.sh