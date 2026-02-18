# Migration Parallel-Run Validation Checklist and Sign-Off

Issue link: #36

## Validation checklist
### Record count checks
- [ ] Customers row count matches expected tolerance.
- [ ] Products row count matches expected tolerance.
- [ ] Sales row count matches expected tolerance for parallel period.
- [ ] Sale items row count matches expected tolerance.

### Spot checks
- [ ] 10 random customers compare key fields.
- [ ] 10 random products compare unit type + price.
- [ ] 10 random sales compare subtotal/tax/total.
- [ ] 10 random sale items compare quantity/weight and line totals.

### Receipt sample checks
- [ ] Regenerate/open 10 receipts from migrated sales.
- [ ] Verify receipt numbers, date/time, and totals.
- [ ] Verify optional customer rendering when present.

## Defect policy during parallel run
- Log defects in GitHub issues with data sample reference.
- Classify severity as blocker/high/medium/low.
- Block cutover on unresolved blockers and high-severity data defects.

## Ready-to-cut-over criteria
All conditions must be true:
- [ ] No open blocker defects.
- [ ] Financial fields validated for sampled transactions.
- [ ] Receipt regeneration works for sampled set.
- [ ] Stakeholder sign-off recorded.