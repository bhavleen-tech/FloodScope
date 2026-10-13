# Multi-page-style navigation update

The homepage now provides six separate workspace options: Area Explorer, Satellite Screening, Impact Assessment, Reports & Validation, Insight Assistant, and Demonstration.

Each workspace has its own view, persistent top navigation, and a Home button. Existing API functionality is preserved. The app remains a single HTML document with view-based navigation (not six separately served HTML files), so map state and uploaded data persist between views. This avoids the old extremely long scrolling dashboard.

The appearance has been revised to a formal white/light-grey institutional design. No claim of government affiliation is made. The hosted pretrained AI integration remains optional; local fallback is rules-based.

Run: `python -m pip install -r requirements.txt` then `python -m uvicorn backend.main:app --reload`.

QA performed: JS syntax, Python syntax, ZIP integrity. Full browser and live satellite testing not performed.
