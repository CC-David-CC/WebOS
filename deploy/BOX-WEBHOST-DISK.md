# box-webhost storage — 2026-11-17 UTC

Both physical drives are SATA SSDs. `/dev/sda2` is the boot filesystem
(SanDisk SDSSDA120G, approximately109GiB usable). `/dev/sdb1` is mounted at
`/srv/data` (Inland SATA SSD, approximately469GiB usable).

The current ksu.codes static release is served by Caddy from
`/srv/data/webos-viewer-releases/<release>/public`. Its retained account/backend
process also runs from a release under that data volume. This inspection did not
move account data, change services or change either website.

The user explicitly authorized deleting retired simplified builds without a
backup.132 unused hash-named static build directories were removed from
`/srv/codi-connected/simplified`. The one referenced by the active beta.ksu.codes
Caddy configuration was retained:
`0965a0cbdd022f588061cdc23e10eb6b18fa5977cc3f6a05569439eaf11d2020`.

Measured free-space increase:74,027,823,104bytes (68.9GiB). Boot free space after
cleanup:79,228,755,968bytes (73.8GiB). The data volume had approximately294GiB
free before the new PdfCraft release. These are observations, not quotas.

Before/after checks verified the active ksu.codes release receipt, beta index,
backend instance and issuer, Caddy configuration bytes and all six service PIDs.
No backups were created for the discarded builds. Inactive historical Caddy
configuration copies may reference discarded releases; they are not valid
rollback instructions. Use the current release's explicit deployment report.

Private exact target list, inventories, authorization and deletion/continuity
receipt are in
`/home/dflanag3/Projects/.webos-migration/pdfcraft-nightly-20261117-7barkpzk/`
(`host-cleanup-plan.json`, `host-cleanup-result.json`, and associated inventories).
No other server cleanup or relocation is implied by this record.
