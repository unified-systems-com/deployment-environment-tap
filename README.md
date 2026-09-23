# deployment-environment-tap

TAP deployment environment: which environment (staging, production, a customer sandbox) a node or
edge belongs to, as a dimension pack. One key per environment — `deployment.environment.<name>` —
valued `member`, so a node shared across environments carries each key it serves.

Read first: `specs/spec-deployment-environment-v0.md`.
