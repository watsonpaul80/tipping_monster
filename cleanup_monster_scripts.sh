#!/bin/bash
# Remove outdated ROI tracker scripts
rm -f track_roi_by_points_dualmode_filtered*.py

# Remove outdated weekly summary generators and viewers
rm -f generate_weekly_summary*.py
rm -f weekly_roi_summary*.py

# Rename final working scripts
mv track_roi_by_points_dualmode_filtered_advised_matched_FINAL.py roi_tracker_advised.py
mv generate_weekly_summary_textfriendly_splitmode.py generate_weekly_summary.py
mv weekly_roi_summary_detailed_filtered_telegram.py weekly_roi_summary.py

echo "🧹 Cleanup complete. Final scripts in place:"
echo "  - roi_tracker_advised.py"
echo "  - generate_weekly_summary.py"
echo "  - weekly_roi_summary.py"
