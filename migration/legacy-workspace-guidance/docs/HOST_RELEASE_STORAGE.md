# Webhost release storage

On 2026-11-02, three inactive public Simplified releases were moved from
`/srv/codi-connected/simplified/` to the existing archive on the larger
`/srv/data` filesystem:

- `e4cec0d0b929cb5f6bdc41e146d433d2d8e99eb5314b5ce5a833ea2c0d280a2f`
- `d5e3b44eb6e6f3d5038d0adbda6ea090455508f2dbb9e7fe236f3bef00849898`
- `d652a17c3d8144db943eeddd48b5bd11e8a66e7364797ab7e70003c9bd758e0c`

They are under `/srv/data/codi-archived-simplified-20261101/<release>`.
Under the hosting controller lock, each source's release name, public cache
manifest ID, file list, lack of symlinks, and absence from current hosting and
Caddy configuration were checked. Each was copied to a temporary archive
directory and compared to the source with an rsync checksum dry run before its
source was removed. These are public static assets, not account data. To use
one for rollback, copy it back to the original release directory and verify
it before activating through the hosting controller.

The active `f4e8c4800dbf92e9796ea7e7b3cdbf64863f83bfccfeef1ef4e78556460c6be7`
and its immediate rollback were left in place; root and `/desktop/` returned
HTTP 200 after the move. Root free space increased from approximately 5.6 to
5.9 GiB. Many releases share hard-linked files, so a directory's apparent size
is not the amount that moving it frees. The release directory
`bfcccab6fcdfd33221aeb5e57dd59d8eb788217b0c0172bb1cf45b3c533a807b`
was deliberately left alone because its name did not match its cache manifest
ID; investigate its provenance before altering it. Keep checking disk space and
never infer that private account data is disposable from release cleanup.
