---
name: contract
description: Generate an Impulse Nutrition partnership contract PDF for an influencer. Asks for athlete details and contract type, then generates a ready-to-sign PDF.
user_invocable: true
---

# Contract Generator Skill

Generate a partnership contract PDF for Impulse Nutrition influencers.

## Instructions

When the user invokes this skill, collect the following information. Use AskUserQuestion to gather what you need. You can ask multiple questions at once.

### Required fields:
1. **Prenom** and **Nom** of the athlete
2. **Adresse** complete
3. **Type de contrat**: dotation (monthly product allocation), ambassadeur (20EUR per unique affiliate use), or paid (fixed budget)
4. **Code d'affiliation** (e.g. "AUGUSTIN")

### Conditional fields:
- If **dotation**: ask for the monthly amount in EUR TTC (e.g. 150)
- If **paid**: ask for the total budget in EUR, and optionally a monthly product dotation amount
- If **ambassadeur**: no amount needed (fixed at 20EUR/use)

### Optional fields (use defaults if not specified):
- Date d'effet: defaults to today (DD/MM/YYYY)
- Duration: defaults to 12 months
- Min stories/month: defaults to 3
- Min reels or posts/month: defaults to 1
- Gender (M/F): defaults to M — used for grammatical agreement (Domicilié/Domiciliée)

## Generation

Once you have all the info, run the script with the venv Python:

```bash
instagram_dm_mcp/.venv/bin/python generate_contract.py \
  --first-name "PRENOM" \
  --last-name "NOM" \
  --address "ADRESSE" \
  --date "DD/MM/YYYY" \
  --duration MONTHS \
  --type TYPE \
  --dotation-amount AMOUNT \
  --budget-amount AMOUNT \
  --code CODE \
  --stories N \
  --reels N \
  --gender M_OR_F
```

The script outputs the path of the generated PDF. Share this path with the user.

If `--dotation-amount` or `--budget-amount` are not applicable, omit them (they default to 0).

## Example

User says: "contract pour Marie Dupont, dotation 150EUR, code MARIE, adresse 5 rue de la Paix 75002 Paris"

```bash
instagram_dm_mcp/.venv/bin/python generate_contract.py \
  --first-name Marie \
  --last-name Dupont \
  --address "5 rue de la Paix, 75002 Paris" \
  --type dotation \
  --dotation-amount 150 \
  --code MARIE \
  --gender F
```
