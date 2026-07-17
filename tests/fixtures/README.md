# Test fixtures

Storage for **anonymized real UDP payloads** captured from an ekey net system,
used to verify the parser against the actual hardware encoding.

## Available fixtures

From a real ekey net capture (terminal server UDP, `rare` format), verified in
[`../test_fixtures.py`](../test_fixtures.py):

| File | Contents |
|------|----------|
| `rare_terminal_reject_unknown.bin` | Rejected/unknown finger (no PII) |
| `rare_terminal_access_granted.bin` | Access, left middle finger (name **anonymized**) |

## Privacy & workflow

- Only **anonymized `.bin` payloads** are committed.
- Raw network captures are kept local and must not be committed — they can
  contain clear names in the payload.
- If a captured payload contains a clear name, anonymize it before committing.
