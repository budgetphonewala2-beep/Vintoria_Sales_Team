# Third-party notices

## ai-sales-team-claude (base project)
- Source: https://github.com/zubair-trabzada/ai-sales-team-claude (revision `efef8b8`)
- Author: Zubair Trabzada — License: MIT (Copyright (c) 2026 Zubair Trabzada). The original licence is kept in `LICENSE`.
- This repository is a modified version: skill content, frameworks, templates, agents and scripts derive from it.

## lead-signal-listener
- Source: https://github.com/yangyixxxx/lead-signal-listener (revision `983fd7b`)
- Author: Yangyi — License: MIT (Copyright (c) 2026 Yangyi)
- Used for (adapted, not copied verbatim): the transparent weighted phrase-scoring approach in
  `skills/sales/scripts/intent_scan.py` (new EN/HI/Hinglish phrase set for service buyers).

## autonomous-sdr
- Source: https://github.com/RodricDib06/autonomous-sdr (revision `8c7c98d`)
- Author: Rodric Dib — License: MIT (Copyright (c) 2026 Rodric Dib)
- Used for (adapted, not copied verbatim): the deterministic claim-extraction and claim/source matching in
  `skills/sales/scripts/claim_check.py` (unicode tokens, stemming, verbatim-quote gate and placeholder check added).

## marketingskills (cold-email)
- Source: https://github.com/coreyhaines31/marketingskills (revision `88c79f6`)
- Author: Corey Haines — License: MIT (Copyright (c) 2025 Corey Haines)
- Used for (adapted, not copied verbatim): the AI-tell / banned-phrase categories in `skills/sales/scripts/email_lint.py`,
  the deliverability stop-loss thresholds (bounce > 2 %, reply rate < 1 % after 300 sends) and warm-up ramp in
  `outreach.py`, the extra reply types (how-did-you-get-my-email, wrong person, send info) and the no-show policy.

MIT License text (applies to each of the above):
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and
to permit persons to whom the Software is furnished to do so, subject to the following conditions: The above
copyright notice and this permission notice shall be included in all copies or substantial portions of the
Software. THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.

## gtm-agents (cold-email-personalization)
- Source: https://github.com/gtmagents/gtm-agents (revision `78e0419`)
- License: Apache License 2.0
- Used for (adapted, not copied verbatim): the 0-100 cold-email scoring dimensions (situation recognition, value
  clarity, personalization, CTA effort, punchiness, subject) and the recipient-to-sender sentence ratio, re-weighted
  and made step-aware in `skills/sales/scripts/email_lint.py`. No files were copied; Apache-2.0 terms apply to the
  original work: https://www.apache.org/licenses/LICENSE-2.0

