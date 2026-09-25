# Claim checks at the reference parameters

Parameters: `outputs/params_reference.json`. 16 Poisson seeds, averaged.

| ID | Kind | Core | Statement | Criterion | Observed | Result |
|---|---|---|---|---|---|---|
| C1 | claim |  | The current expectation concerns the ongoing activity (low in calm, higher in dense activities). | late in blocks, current expectation lower in calm than in dense activities | calm 0.61 vs dense 1.88 (true 0.5 vs 2.0) | PASS |
| C2 | claim |  | The habitual expectation concerns daily life as a whole. | habitual expectation lies between calm and dense rates | 1.01 (24-h mean rate 0.87) | PASS |
| S1 | sanity | yes | Poisson noise does not inflate the expectation (false alarms of the surprise rule stay rare). | without use, 24-h mean expectation with noise within 10% of the same model without noise | ratio 1.064 | PASS |
| C11 | claim |  | A calm activity may fall slightly short of what is expected, even without social media use. | without use or noise, mismatch index in calm activities > 0.05 events/min | 0.28 events/min | PASS |
| C3 | claim | yes | Entering the stream is highly surprising, so the current expectation quickly approaches the stream's rate (calibration). | after 2 min in the stream, >= 60% of the gap closed (session starting from a calm activity; from a dense one reported) | from calm 105%; from dense 62% | PASS |
| C4 | claim | yes | After the stream is left, the current expectation falls back only gradually (after-effect). | excess expectation after a 10-min session decays to 1/e in 15-90 min | 19 min | PASS |
| C4b | claim | yes | Leaving the stream is surprising too, but this does not speed up the fall: a denser stream does not shorten the after-effect. | 1/e decay >= 15 min after streams at 4, 16 and 32 events/min | 4: 18 min / 16: 19 min / 32: 20 min | PASS |
| C5 | claim |  | The mismatch is largest when the next activity is calm. | same session and preceding activity: mismatch index in the next 30 min larger if that activity is calm than dense | calm 4.08 vs dense 3.59 events/min | PASS |
| C6 | claim |  | Each session adds a little to the habitual expectation. | one isolated session: < 5% by the end of the day; one session a day for 28 days: > 5% | isolated +3.9%; one a day for 28 days +12% | PASS |
| C7 | claim | yes | The habitual expectation rises over days with the number of sessions. | after 7 days, habitual expectation rises with 1 < 4 < 8 < 16 sessions of 10 min per day | 1: 1.12 / 4: 1.51 / 8: 2.03 / 16: 2.94 | PASS |
| M1 | property |  | At equal number and length, sessions that overlap add less to the habitual expectation than spaced ones. | 8 x 10 min per day, gaps of 10 / 30 / 110 min (reported, not stated in the manuscript) | gap 10 min: 1.49 / gap 30 min: 1.81 / gap 110 min: 2.04 | PASS |
| C8 | claim | yes | A raised habitual expectation holds the current expectation above what calm activities deliver, even with no recent session. | after 14 days of 16 x 10 min/day, mismatch index on waking (before any session) > 2 x no-use and > 0.1 events/min | 0.37 vs 0.04 events/min | PASS |
| C9 | claim | yes | This persistence fades when the pattern of use changes, over days rather than minutes. | after use stops, habitual half-recovery between 1 and 14 days; calm mismatch index lower after 3 days | half-recovery 2.4 d; calm mismatch 2.00 -> 0.46 | PASS |
| C10 | claim |  | The downward weight is smaller in dense activities, so the habitual expectation does not hold the current one down during use. | after 60 min in the stream, current expectation >= 90% of the stream's rate | 99% | PASS |
| P1 | claim |  | A higher within-session relevance rate raises the habitual expectation. | stream at 4 / 8 / 16 events/min -> higher habitual expectation after 7 days | 1.29 / 2.03 / 3.46 | PASS |
| P2 | claim |  | Session length raises the expectation until a ceiling that sessions of ordinary duration already reach. | a 10-min session reaches >= 90% of the level reached by a 40-min session | 2 min 55% / 5 min 98% / 10 min 107% / 20 min 106% / 40 min 100% | PASS |
| P3 | claim |  | At equal total time, fragmentation raises the habitual expectation (up to a ceiling). | habitual after 7 days: 1x160 < 4x40 < 16x10 (32x5 reported) | 1 x 160 min 1.79 / 4 x 40 min 2.06 / 16 x 10 min 2.94 / 32 x 5 min 3.11 | PASS |
| P4 | claim |  | Chronicity raises the habitual expectation, which then saturates. | habitual rises over 1/3/7/14 days; gain 14->28 d smaller than 3->7 d | 1 d 1.58 / 3 d 2.35 / 7 d 2.94 / 14 d 3.15 / 28 d 3.23 | PASS |
| P5 | claim |  | At equal total time, fragmented use raises the current expectation averaged over the whole day. | all-day mean current expectation >= 1.2 x higher for 16 x 10 min than for 1 x 160 min | fragmented / concentrated = 1.62 | PASS |

Kinds: `claim` = stated in the manuscript; `sanity` = validity check of the simulation; `property` = model behaviour reported for transparency. Core = claims the manuscript's argument rests on. Mismatch index = per-trajectory max(mu1 - lambda, 0), averaged.
