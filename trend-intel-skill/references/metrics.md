# Metrics

## Purpose

Define platform-agnostic trend scoring fields.

## Core Metrics

- `stars_period`: short-window growth signal.
- `forks_total`: practical adoption proxy.
- `stars_total`: baseline popularity.
- `contributors`: optional collaboration signal.

## Score Formula

`hot_score = 0.55 * period_norm + 0.25 * forks_norm + 0.20 * total_norm`

Normalize each metric by dividing by max value in current batch.

## Trend Type

- `breakout`: `period_norm >= 0.70`
- `steady`: `0.35 <= period_norm < 0.70`
- `potential`: `period_norm < 0.35`

Update this file first when changing score logic.
