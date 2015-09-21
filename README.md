# zshadow
A shell script for FreeBSD that automates replication of ZFS datasets

The goals of **zshadow** are as follows

  * zero dependencies on a FreeBSD system
  * automatically send ZFS snapshots to remote pools
  * recover from previously failed sends without intervention
  * preserve deleted datasets on remote copies

# setup
Create a remote dataset that will serve as the root of your backups:

    root@crypt:/ # zfs create -o mountpoint=none -o atime=off vault/shadows

The above created a '**shadows**' dataset on the pool named '**vault**'. It
also set the following properties:

  * **mountpoint**: this is set to '**none**' so that the dataset can't
    be mounted. If the dataset were mounted, it's likely that the contents
    would be modified, invalidating **zshadow**'s incremental backups
  * **atime**: this is set to '**off**' to further protect the remote
    datasets from modification
