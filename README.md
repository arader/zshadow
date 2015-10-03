# zshadow
A shell script for FreeBSD that automates replication of ZFS datasets

The goals of **zshadow** are as follows

  * zero dependencies on a FreeBSD system
  * automatically send ZFS snapshots to remote or local pools
  * preserve deleted datasets on remote copies
  * recursively sends child datasets, with the option to skip datasets
  * support sending datasets to multiple targets
  * allow for different 'send schedules' for different targets
    (hourly, daily, etc)
  * use 'tagging' mechanism for configuring replication
  * store configuration data in ZFS properties
  * recover from most previously failed sends without intervention
  * maintain a single reference snapshot for incremental sends

# Overview
The **zshadow** script is a single shell script that is designed to have
zero dependencies on a FreeBSD system. No installation is necessary, just
copy the script down and you can start using it.

**zshadow** is meant for people with a simple goal: anyone that has a
collection of ZFS datasets that wants to replicate them. The script is
designed to support this goal in a number of flexible ways.

For example, say you have a pool named 'tank' and you want every dataset
in that pool except one to go to a remote machine for safe keeping, **zshadow**
supports that.

## Concepts
The concepts used by **zshadow** are meant to be easily understood. A
complicated backup strategy is never a good idea. To that end, **zshadow**
uses a concept of 'tagging' datasets for sending.

### Tags
A **tag** is a named set of configuration options used for sending datasets. For
example, you might have a tag named 'UK-mirror' that stores the options necessary
for sending ZFS datasets from your local machine to a machine in the UK using
**ssh** as the transfer mechanism.

After creating a tag, you can apply that tag to any number of datasets across
any number of pools.

When you invoke the **zshadow** script with the 'send' command, you tell it
which tags you want to send.

### Sending
When you use **zshadow**'s send command you give it a list of tags to send.
**zshadow** then looks for every dataset marked with those tags, updates the
local snapshots, and then sends them based on that tag's configuration.

Different tags have different methods of sending snapshots. For example, one
tag might be configured to use **ssh** to send snapshots, where as another
might store snapshots in a local pool. This is meant to be extensible, so
later versions of **zshadow** could support more exotic transfer mechanisms.

# Using zshadow

## Setup
Create a remote or local dataset that will serve as the root of your backups:

    root@crypt:/ # zfs create -o mountpoint=none -o atime=off vault/shadows

The above created a '**shadows**' dataset on the pool named '**vault**'. It
also set the following properties:

  * **mountpoint**: this is set to '**none**' so that the dataset can't
    be mounted. If the dataset were mounted, it's likely that the contents
    would be modified, invalidating **zshadow**'s incremental backups
  * **atime**: this is set to '**off**' to further protect the remote
    datasets from modification

## Create a tag
Now that you have a place to store your snapshots, you need to create a tag
that contains the configuration options necessary to send your snapshots to it.

### Local replication
The simplest form of replication is to the local machine. The only option needed
is the name of the local dataset that the replications should be stored in:

    root@host:/ # zshadow create local-mirror -s local -o target=vault/shadows

The above created a tag named **local-mirror** using the **local** scheme. The
only option provided is the target dataset for sends. In this example sending
the local dataset 'tank/myfiles' will result in the snapshot being replicated to
'vault/shadows/tank/myfiles' on the local machine.

### Remote replication
For replication snapshots to a remote machine, **ssh** is used as the mechanism
for gettings bits from your local machine to the remote host. To that end, a tag
using **ssh** is going to require a few more options than datasets that are
replicated locally:

    root@host:/ # zshadow create UK-mirror -s ssh -o target=vault/shadows \
      -o host=uk-backups.example.com -o user=keeper

The above created a tag named **UK-mirror** using the **ssh** scheme. The options
supplied for the tag are:

  * **target**: this specifies the root dataset that will store all of the
    replicated snapshots and their datasets. In this example sending the
    local dataset 'tank/myfiles' will result in the snapshot being replicated
    to 'vault/shadows/tank/myfiles' on the remote machine
  * **host**: the remote host to use for **ssh**
  * **user**: the user to use for **ssh**, note that this user must have
    sufficient permissions to receive the ZFS snapshots

## Tag your datasets
Now that you've created at least one tag, you need to define which datasets
that tag applies to. Datasets can be tagged using the **tag** command.

    root@host:/ # zshadow tag tank/files UK-mirror

The above tagged the 'tank/files' dataset with the 'UK-mirror' tag. Now
if the 'UK-mirror' tag were to be sent using **zshadow send** the 'tank/files'
dataset (and all its children!)  would have a snapshot taken and replicated.

A dataset can have any number of tags applied to it, with each tag having
a "**mode**" to go with it.

### Tag modes
Tags on a dataset aren't just a binary yes/no flag. Instead, it is a full
property that has a value.

This value is used to tell **zshadow** how to treat this dataset when that
particular tag is being sent.

#### Send mode
The default tag mode is '**send**'. This causes the dataset to have a
snapshot taken and to be replicated whenever that tag is being sent by
**zshadow**.

The send mode of a tag is inherited, meaning all children datasets of a
dataset tagged in '**send**' mode will also be sent.

To explicitly set the tag mode to '**send**', use the following:

    root@host:/ # zshadow tag tank/files UK-mirror -m send

#### Ignore mode
Antithetical to the '**send**' mode of a tag is the '**ignore**' mode.
This tag mode causes the dataset and its children to explicitly be
ignored whenever **zshadow** is sending the tag.

This is incredibly useful when you want to replicate an entire pool,
except for one or two datasets.

To use the '**ignore**' mode, use the following:

    root@host:/ # zshadow tag tank/files UK-mirror -m ignore

With this, the 'tank/files' dataset (and all its children!) will be
explicitly skipped when the 'UK-mirror' tag is sent.

## Send your tags
To send your tags, use the **send** command:

    root@host:/ # zshadow send

The above will send every tag you've created. If you'd like to send
only specific tags, you can specify them:

    root@host:/ # zshadow send local-mirror UK-mirror

This allows you to have different send schedules for each tag. You
could have an hourly cron job run the local-mirror send, and a daily
one run the UK-mirror send.

## Checking status
The **list** command can be used to see what tags exist, what datasets
are tagged, and when each dataset was last sent:

    root@host:/ # zshadow list
    TAG           DATASET               LAST SENT
    local-mirror  tank/files            Sat Oct  3 10:09:33 PDT 2015
    local-mirror  tank/files/important  Sat Oct  3 10:29:15 PDT 2015
    UK-mirror     tank/files            Sat Oct  3 10:32:07 PDT 2015
    UK-mirror     tank/files/important  Sat Oct  3 11:09:52 PDT 2015
    CH-mirror     tank/files            -
    CH-mirror     tank/files/important  -

In the above output you can see the tags, their datasets, and the times
for each replication. The last two have never been sent, due to the '-'
in the LAST SENT column

## Help
Use the **zshadow help** command to get a breakdown of what commands
are available. Use **zshadow help <command>** to get detailed help,
including the list of options, for a specific command.
