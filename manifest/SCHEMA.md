# Mod manifest schema (manifest/mods.yaml)
Each entry:
- id: slug (modrinth/curseforge slug)
  name: Display name
  category: foundation|perf|qol|combat|magic|tech|worldgen|dimension|boss|npc|quests|ui|audio|cosmetic|library
  status: CONFIRMED|CANDIDATE|CUSTOM|REJECTED
  source: curseforge|modrinth|custom
  project_id: numeric/slug (required for CONFIRMED)
  file_id: exact file id (required for CONFIRMED)
  version: exact version string
  side: client|server|both
  deps: [ids]
  perf_cost: low|med|high
  purpose: why it is in the pack
  notes: conflicts / reasons for rejection
  verified_on: date + by whom
Pack-level header: mc_version, loader, loader_version, java, manifest_version (semver).
