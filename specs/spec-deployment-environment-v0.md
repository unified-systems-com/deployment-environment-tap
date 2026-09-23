# TAP Deployment Environment Plugin Specification

**Which environment — staging, production, a customer sandbox — a node or edge belongs to, as a dimension
pack: one key per environment, `deployment.environment.<name>`, valued `member`.**

## Plugin Identity

| Field | Value |
| --- | --- |
| Slug | `deployment_environment` |
| Display name | TAP Deployment Environment |
| Description | Environment membership as a dimension pack: one key per environment (`deployment.environment.<name>`, valued `member`), so a node shared across environments carries every key it serves. |
| Kind | Vocabulary substrate with no models (a dimension pack), like `dcom`. Consumes nothing; consumed by any plugin whose nodes are placed in an environment (highbar first). |

This plugin ships no TAP-managed types, so it declares no default dimensions; the pack's own nodes carry
core's `tap.meta: dimension`.

## Philosophy

A designed system is usually built more than once: a staging copy, a production copy, sandboxes for people
to break. The copies share most of their shape and some of their parts. A reader who cannot tell which copy
a node belongs to cannot answer "what does production look like", and a node that serves several copies —
an identity provider, a code host — has to be able to say so.

**One key per environment, not one value per node.** An entity's dimensions hold one value per key, so a
single `environment: staging` key cannot express a node that serves staging *and* production. The pack
therefore puts the environment in the key: `deployment.environment.staging`, `deployment.environment.production`,
each valued `member`. A shared node carries each key it serves. Ruled by George 2026-09-22: this makes
cross-environment entities explicit instead of establishing a convention that "no value means all".

**Absence means absence.** A node without `deployment.environment.production` is not placed in production
(or has not been observed there) — never "shared by default". This is the three-states stance applied: no
key is unobserved, the key present is membership.

**The value is `member` in v0.** The key's presence is the fact. A richer value (a role such as primary or
replica) was considered and deferred: a fixed marker can grow into a vocabulary later without renaming any
key, and "shared" is already derivable by counting a node's environment keys.

**Aligned with OpenTelemetry.** OTel's `deployment.environment.name` attribute carries the environment as a
value; the OTel value `staging` maps one-to-one to this pack's key `deployment.environment.staging`, so an
import is mechanical.

Nothing here says what KIND of fact a node is — that is `dcom`'s axis, and the two combine freely: a node is
`dcom: design` + `deployment.environment.staging: member` while it is planned, and
`dcom: configuration` + the same key once built.

**Provenance markers:** the pack's nodes are *documented* vocabulary; which nodes carry which key is
*designed* (seeded) or *observed* (collected) by the consuming plugin.

## Goals

| # | Name | Description |
| --- | --- | --- |
| 1 | Membership Per Environment | Any node or edge can say which environments it belongs to, several at once. |
| 2 | One Query Per Environment | "Everything in production" is a single key-presence predicate. |

## Requirements

| RID | Name | Status | Notes |
| --- | --- | --- | --- |
| req-deployment-environment-keying | [Keying Rule](#keying-rule) | Implemented | Key per environment, value `member`; shared nodes carry each key; absence is not "all" |
| req-deployment-environment-pack | [The Dimension Pack](#the-dimension-pack) | Implemented | Family node plus `staging` and `production` keys; other environments mint on first use |
| req-deployment-environment-record | [CI Record and Tests](#ci-record-and-tests) | Implemented | The `ci` record seeds the pack; tests import it into a grid |

---

### Keying Rule
----
RID: `req-deployment-environment-keying`

Status: `Implemented`

An entity belonging to environment `<name>` carries the dimension key `deployment.environment.<name>` with the
value `member`. A node serving several environments carries one key per environment. The bare family name
`deployment.environment` is never a key on an entity. A missing key means the entity is not placed in (or not
observed in) that environment.

#### Implementation

Consumers stamp the key in the entity's `dimensions` map (a GRIFT bundle's `entity.dimensions`, or a model's
`DEFAULT_DIMENSIONS` when every row of a type belongs to one environment). Read a side of the grid by key
presence, with the key in brackets because its dots are part of the key: `MATCH (n) WHERE n.dimensions["deployment.environment.production"] IS NOT NULL RETURN n`. The unbracketed path `n.dimensions.deployment.environment.production` is read as nested keys and silently matches nothing (observed 2026-09-22: `n.dimensions.tap.cloud IS NOT NULL` returned 0 accounts, `n.dimensions["tap.cloud"] IS NOT NULL` returned 1).

#### Acceptance Criteria

| ACID | Title | Status | Description | Notes |
| --- | --- | :---: | --- | --- |
| req-deployment-environment-keying-1 | Rule Stated On Every Node | Implemented | Every pack node's description states the key-per-environment rule and the `member` value. | |
| req-deployment-environment-keying-2 | Family Is Not A Key | Implemented | The family node states entities never carry the bare family name as a key. | |
| req-deployment-environment-keying-3 | Query Form Is Bracketed | Implemented | Every documented query addresses the key as `n.dimensions["deployment.environment.<name>"]`, never the dotted path. | |

---

### The Dimension Pack
----
RID: `req-deployment-environment-pack`

Status: `Implemented`

`grift/dimensions.grift.json` seeds three `dimension` nodes: `deployment.environment` (the family, carrying the
scheme), `deployment.environment.staging` and `deployment.environment.production`. No edges. There are no value
nodes: a fixed `member` value has nothing to describe. Other environments — a customer sandbox — mint their own
`deployment.environment.<name>` key on first use; the pack does not pre-seed them.

#### Acceptance Criteria

| ACID | Title | Status | Description | Notes |
| --- | --- | :---: | --- | --- |
| req-deployment-environment-pack-1 | Three Nodes | Implemented | Importing the pack yields exactly the family node and the two environment keys. | |
| req-deployment-environment-pack-2 | Idempotent | Implemented | Re-importing leaves one row per name. | |

---

### CI Record and Tests
----
RID: `req-deployment-environment-record`

Status: `Implemented`

`boot/ci.boot.json` installs this plugin alone (it declares no dependencies) and seeds the pack; the consumer
flips self to editable. `tests/test_deployment_environment_pack.py` imports the pack through `grift_import` and
asserts on the `dimension` rows; `tests/test_deployment_environment_manifest.py` runs `validate_plugin` at
structure and strict levels.

#### Acceptance Criteria

| ACID | Title | Status | Description | Notes |
| --- | --- | :---: | --- | --- |
| req-deployment-environment-record-1 | Record Declared | Implemented | The manifest declares the `ci` record with its sha256. | |
| req-deployment-environment-record-2 | Validates Strict | Implemented | `validate_plugin --strict` passes on the package. | |
