# Golden set v1.0

Status: frozen. 40 fictional cases, approved by project_owner on 2026-11-05, under SRC-011.

Use [manifest.json](manifest.json) for versions, case IDs, frozen splits, and hashes. The [approval record](approval.json) preserves the explicit human acceptance.

Only inputs/development.jsonl and inputs/evaluation.jsonl are classifier inputs. Each record contains exactly case_id and transcript. Expected labels and review metadata are in separate answer and audit artifacts. Never send the whole release folder to the classifier.

Use development cases for prompt development. Keep evaluation cases out of prompt demonstrations. The source candidate snapshot remains unchanged and pending as historical provenance; the separate approval record and approved gold records establish subsequent acceptance.

This small synthetic set does not establish operational accuracy. No model evaluation has run. Create a new release version for corrections; preserve this release.
