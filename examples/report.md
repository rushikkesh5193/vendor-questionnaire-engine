# Vendor questionnaire scoring

Scores come from an original SIG/CAIQ-style question set (not the SIG or CAIQ). *Claimed* takes answers at face value; *verified* gives an unsupported yes only partial credit.

| Vendor | Tier | Claimed | Verified | Rating | Weakest domains |
|---|---|---|---|---|---|
| Vendor 004 (`V004`) | 2 | 16.9 | 16.9 | high | Access control, Resilience, Data protection |
| Vendor 001 (`V001`) | 2 | 95.6 | 95.6 | medium | Access control, Resilience, Data protection |
| Vendor 008 (`V008`) | 2 | 95.6 | 95.6 | medium | Data protection, Access control, Resilience |
| Vendor 005 (`V005`) | 2 | 97.1 | 97.1 | low | Fourth parties, Access control, Resilience |
| Vendor 007 (`V007`) | 2 | 97.1 | 97.1 | low | Resilience, Access control, Data protection |
| Vendor 002 (`V002`) | 2 | 100.0 | 97.8 | low | Governance, Access control, Resilience |
| Vendor 006 (`V006`) | 2 | 100.0 | 98.5 | low | Vulnerability management, Access control, Resilience |
| Vendor 011 (`V011`) | 4 | 100.0 | 100.0 | low | Access control, Resilience, Data protection |
| Vendor 012 (`V012`) | 1 | 100.0 | 100.0 | low | Access control, Resilience, Data protection |
| Vendor 013 (`V013`) | 2 | 100.0 | 100.0 | low | Access control, Resilience, Data protection |
| Vendor 014 (`V014`) | 3 | 100.0 | 100.0 | low | Access control, Resilience, Data protection |
| Vendor 015 (`V015`) | 4 | 100.0 | 100.0 | low | Access control, Resilience, Data protection |
| Vendor 016 (`V016`) | 1 | 100.0 | 100.0 | low | Access control, Resilience, Data protection |
| Vendor 017 (`V017`) | 2 | 100.0 | 100.0 | low | Access control, Resilience, Data protection |
| Vendor 018 (`V018`) | 3 | 100.0 | 100.0 | low | Access control, Resilience, Data protection |
| Vendor 019 (`V019`) | 4 | 100.0 | 100.0 | low | Access control, Resilience, Data protection |
| Vendor 020 (`V020`) | 1 | 100.0 | 100.0 | low | Access control, Resilience, Data protection |
| Vendor 021 (`V021`) | 2 | 100.0 | 100.0 | low | Access control, Resilience, Data protection |
| Vendor 022 (`V022`) | 3 | 100.0 | 100.0 | low | Access control, Resilience, Data protection |
| Vendor 023 (`V023`) | 4 | 100.0 | 100.0 | low | Access control, Resilience, Data protection |
| Vendor 024 (`V024`) | 1 | 100.0 | 100.0 | low | Access control, Resilience, Data protection |
| Vendor 025 (`V025`) | 2 | 100.0 | 100.0 | low | Access control, Resilience, Data protection |
| Vendor 026 (`V026`) | 3 | 100.0 | 100.0 | low | Access control, Resilience, Data protection |
| Vendor 027 (`V027`) | 4 | 100.0 | 100.0 | low | Access control, Resilience, Data protection |
| Vendor 028 (`V028`) | 1 | 100.0 | 100.0 | low | Access control, Resilience, Data protection |
| Vendor 029 (`V029`) | 2 | 100.0 | 100.0 | low | Access control, Resilience, Data protection |
| Vendor 030 (`V030`) | 3 | 100.0 | 100.0 | low | Access control, Resilience, Data protection |
| Vendor 003 (`V003`) | 2 | - | - | unrated | Access control, Data protection, Governance |

## Issues

### High (12)

- **CRITICAL_CONTROL_MISSING** Vendor 001 (`V001`): ACC-3 answered no: Is multi-factor authentication enforced for all privileged and administrator accounts?
- **INCONSISTENT_ANSWERS** Vendor 001 (`V001`): ACC-1 yes but ACC-3 no: claims MFA for all remote access but no MFA for privileged accounts.
- **UNSUPPORTED_YES** Vendor 002 (`V002`): GOV-2 answered yes but no iso27001_cert is on file.
- **CRITICAL_CONTROL_MISSING** Vendor 004 (`V004`): ACC-3 answered no: Is multi-factor authentication enforced for all privileged and administrator accounts?
- **CRITICAL_CONTROL_MISSING** Vendor 004 (`V004`): DAT-1 answered no: Is our data encrypted at rest?
- **CRITICAL_CONTROL_MISSING** Vendor 004 (`V004`): INC-1 answered no: Do you have a documented incident response plan?
- **RATING_HIGH** Vendor 004 (`V004`): Verified score 16.9 is below 60.
- **INCONSISTENT_ANSWERS** Vendor 005 (`V005`): SUB-2 yes but SUB-1 no: claims to flow down obligations to third parties but keeps no list of them.
- **INCONSISTENT_ANSWERS** Vendor 005 (`V005`): SUB-3 yes but SUB-1 no: claims to assess third parties but keeps no list of them.
- **INCONSISTENT_ANSWERS** Vendor 007 (`V007`): BCP-2 yes but BCP-1 no: claims DR is tested but says no DR plan exists.
- **CRITICAL_CONTROL_MISSING** Vendor 008 (`V008`): DAT-1 answered no: Is our data encrypted at rest?
- **INCONSISTENT_ANSWERS** Vendor 008 (`V008`): DAT-3 yes but DAT-1 no: claims managed encryption keys but says data is not encrypted at rest.

### Medium (2)

- **INCOMPLETE** Vendor 003 (`V003`): Only 50.0% of the questionnaire weight is answered (minimum 80%).
- **UNSUPPORTED_YES** Vendor 006 (`V006`): VUL-3 answered yes but no pentest_report is on file.

