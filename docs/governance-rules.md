# Fabric Governance — Source Rules

> **Purpose:** This document is the machine-readable **source of truth** for the
> naming, organization, and access-group rules enforced by the Fabric Governance
> application in this repo. It describes a reference governance model that any
> organization can adopt or adapt. Edit this file to evolve the standard; the
> policy files (`rules/policy.yaml`) and rule engine read from the same rules.

---

## 1. Organizational Hierarchy

```
Fabric Tenant
│
├── Domain IT
│   ├── Sub Domain DEV   → Workspaces (Ws1, Ws2, Ws3)
│   ├── Sub Domain SIT   → Workspaces (Ws4, Ws5, Ws6)
│   └── Sub Domain PRD   → Workspaces (Ws7, Ws8, Ws9)
│
└── Domain BU
    ├── Sub Domain BU 1  → Workspaces (Ws10, Ws11)
    └── Sub Domain BU 2  → Workspaces (Ws12, Ws13)
```

**Key principles:**
- Two top-level domain types: **IT** (split by environment) and **BU** (split by business unit).
- Sub-domains under IT are environment-based (DEV, SIT, PRD).
- Sub-domains under BU are business-unit based.
- Workspaces always live under a sub-domain.

---

## 2. Domain Catalog — 19 Approved Domains

This reference model defines 19 business domains. The domain **codes** are the
governed values (referenced by every workspace manifest); the descriptions are
illustrative and can be re-mapped to your organization's functions.

| # | Business Function | Domain Code |
|---|---|---|
| 1 | Consumer (B2C) Segment Management | `dom-seg-b2c` |
| 2 | Business (B2B) Segment Management | `dom-seg-b2b` |
| 3 | Finance | `dom-ges-fin` |
| 4 | Planning, Control & Assurance | `dom-pln-cnt` |
| 5 | People & Organization | `dom-pss-org` |
| 6 | IT - Data Management | `dom-ops-dat` |
| 7 | Engineering & Network | `dom-eng-net` |
| 8 | AI | `dom-ops-aic` |
| 9 | Logistics | `dom-ops-lgs` |
| 10 | Field Force | `dom-ops-wfm` |
| 11 | Wholesale | `dom-ops-whs` |
| 12 | Contact Center Operations | `dom-cnt-ctr` |
| 13 | Business Operations | `dom-ops-b2b` |
| 14 | Offer / Product | `dom-prd-ofr` |
| 15 | Consumer Commercial Operations | `dom-ops-b2c` |
| 16 | Digital | `dom-exp-dig` |
| 17 | Compliance & Data Privacy | `dom-cmp-prv` |
| 18 | Regulatory, Competition & Legal | `dom-reg-jur` |
| 19 | Internal Audit | `dom-aud-int` |

---

## 3. Naming Conventions

### 3.1 Domain

```
Pattern: dom-<area>-<product>
Regex:   ^dom-[a-z]{2,4}-[a-z0-9]{2,6}$
```

### 3.2 Sub Domain

```
Pattern: sdm-<area>-<product>
Regex:   ^sdm-[a-z]{2,4}-[a-z0-9]{2,6}$
```

### 3.3 Workspace — **STRICT 6-SEGMENT FORMAT**

```
Pattern: <country>-<area>-<subject>-<dataproducttype>-<env>-<suffix>
```

| Segment | Max Length | Description | Allowed Values / Examples |
|---|---|---|---|
| `country` | 2 | ISO 3166-1 Alpha-2 country code, lowercase | `pt`, `fr`, `es` |
| `area` | 4 | Area responsible for the product | `intl` (AI/GenAI), `nlyt` (Analytics), `fops` (FinOps), `dsci` (Data Science), `mrkt` (Marketing) |
| `subject` | 8 | Context describing what aspect of the data product is captured | `sales`, `customer`, `billing`, `network` |
| `dataproducttype` | 3 | Type of the data product | `brz` (bronze), `slv` (silver), `gld` (gold), `ndf` (non-differentiated) |
| `env` | 3 | Environment / context | `poc`, `dev`, `sit`, `uat`, `stg`, `prd` |
| `suffix` | 6 | Random ID for uniqueness | `12fas2` |

**Constraints across all segments:** lowercase only, no special symbols, no
spaces. Numeric chars allowed only in `suffix`.

**Regex (subject up to 8):**
```
^[a-z]{2}-[a-z]{2,4}-[a-z]{2,8}-[a-z]{2,3}-[a-z]{3}-[a-z0-9]{1,6}$
```

### 3.4 Example Workspace Names

```
pt-nlyt-customer-slv-dev-12fas2
pt-mrkt-campaign-gld-prd-a1b2c3
pt-fops-billing-brz-sit-x9y8z7
```

---

## 4. Access Groups — Naming Convention

```
Pattern: grp_<service>_<environment>_<profile>
```

| Segment | Description | Allowed Values |
|---|---|---|
| `grp` | Fixed literal | `grp` |
| `service` | Fabric service | `fabric`, `powerbi` |
| `environment` | Environment | `dev`, `sit`, `uat`, `prd` |
| `profile` | Profile = `<area>_<role>` (area + role joined by `_`) | area: `aic`, `mkt`, `b2c`, `cor`, ...; role: `admin`, `member`, `contributor`, `viewer` |

### 4.1 Examples

| Profile Description | Group Name |
|---|---|
| Administrator of Fabric for corporate data on development | `grp_fabric_dev_cor_admin` |
| Member of Fabric for Marketing department on production | `grp_fabric_prd_mkt_member` |
| Viewer of Power BI for AIC team on test (UAT) environment | `grp_powerbi_uat_aic_viewer` |

**Regex:**
```
^grp_(fabric|powerbi)_(dev|sit|uat|prd)_[a-z]{2,5}_(admin|member|contributor|viewer)$
```

---

## 5. Design Notes

### Live owner-group validation

With `LIVE_CHECKS=true`, the shared rule engine checks each Group owner's
`identifier` using Microsoft Graph `GET /groups/{id}?$select=id`. Configure
an appropriate application permission, such as `Group.ReadBasic.All`, with
admin consent on the GitHub OIDC service principal. This permission reads basic
properties of all tenant groups; it is not limited to the demo group.

- HTTP 200 with the requested group ID produces an `owner-groups-exist` info finding.
- HTTP 404 is a blocking group-not-found finding.
- Authentication, permission, network, service, and malformed-response errors
  block validation rather than being skipped or reported as a missing group.
- With `LIVE_CHECKS` absent or `false`, no group lookup is made.

This verifies group existence only, not membership, the human owner, capacity,
or effective Fabric permissions. The manifest's `groupName` is optional
and is not compared with the directory display name. If supplied, it must
match the schema's naming pattern. For an existing group with a different
name, omit this optional field instead of supplying a fictitious name or
weakening the schema; the Object ID still identifies the group.

Run the offline regression tests from the repository root:
`python -m unittest discover -s tests -p test_live_group_validation.py`.

### Model considerations

- **Domain vs. sub-domain:** domains are the coarse-grained business capability;
  sub-domains partition a domain (by environment for IT, by business unit for BU).
- **Medallion layers:** `dataproducttype` (`brz`/`slv`/`gld`/`ndf`) captures the
  data product's refinement stage; keep it consistent with your lakehouse layering.
- **Area & subject allow-lists** are soft (warn-level) so teams can extend them
  via pull request without a code change — see `rules/policy.yaml`.
- **Mapping organizational sub-domains to the `env` segment:** align the workspace
  `env` value (`poc`/`dev`/`sit`/`uat`/`stg`/`prd`) with the sub-domain lifecycle
  stage the workspace belongs to.
