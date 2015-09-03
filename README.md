# zfshadow
A shell script for FreeBSD that automates replication of ZFS datasets

The goals of *zfshadow* are as follows
  * zero dependencies on a FreeBSD system
  * automatically send ZFS snapshots to remote pools
  * recover from previously failed sends without intervention
  * preserve deleted datasets on remote copies

The last bullet is the primary reason for *zfshadow*'s existence. When
researching zfs replication tools, it became apparent that most rely
on zfs' built-in replication flag. While handy, this has one unfortunate
side effect: an accidentally deleted dataset on your primary pool would
also be deleted on your remote backup. *zfshadow* doesn't have this side
effect.
