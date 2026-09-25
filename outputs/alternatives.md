# Alternative mechanisms

| Model | Passed | Of | Failed | S1 noise inflation | C4 fall (stream 8) | C4b fall (streams 4/16/32) | C8 mismatch, no session |
|---|---|---|---|---|---|---|---|
| Reference (Box 3) | 18 | 18 | none | ratio 1.071 | 19 min | 4: 18 min / 16: 19 min / 32: 20 min | 0.38 vs 0.05 events/min |
| A1 sign-dependent learning rate | 13 | 18 | C2 S1 C4b C6 C8 | ratio 1.900 | 16 min | 4: 14 min / 16: 18 min / 32: 19 min | 1.02 vs 0.90 events/min |
| A2 long-window surprise, both directions | 12 | 18 | S1 C4 C4b C6 C8 P5 | ratio 1.187 | 2 min | 4: 4 min / 16: 1 min / 32: 1 min | 0.23 vs 0.12 events/min |
| A3 surprise speeds up decreases too | 17 | 18 | C4b | ratio 1.052 | 19 min | 4: 18 min / 16: 8 min / 32: 1 min | 0.36 vs 0.05 events/min |
| A4 no downward prediction | 15 | 18 | S1 C6 C8 | ratio 1.108 | 20 min | 4: 20 min / 16: 20 min / 32: 20 min | 0.08 vs 0.32 events/min |

# Fixed versus precision-weighted downward weight

| Downward weight | C8 mismatch on waking, after 14 days of use | same, never used | C10 expectation after 60 min of use (%) | Claims passed |
|---|---|---|---|---|
| fixed 0.0040 | 0.06 | 0.25 | 95.0 | 17 |
| fixed 0.0070 | 0.16 | 0.16 | 91.0 | 17 |
| fixed 0.0100 | 0.27 | 0.11 | 87.0 | 17 |
| fixed 0.0130 | 0.37 | 0.09 | 83.0 | 17 |
| fixed 0.0167 | 0.47 | 0.1 | 79.0 | 17 |
| fixed 0.0250 | 0.67 | 0.06 | 76.0 | 15 |
| precision-weighted (reference) | 0.37 | 0.04 | 99.0 | 18 |

A fixed weight trades persistence in calm activities (C8) against tracking of the stream (C10). None of the fixed values examined (0.004 to 0.025), with other parameters at reference, passes every claim; the precision-weighted weight obtains both. This result depends on the mismatch index being computed per trajectory; with an index computed after averaging trajectories, a fixed weight of about 0.007 also passes every claim, with a persistence effect about half as large.
