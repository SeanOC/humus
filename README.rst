=====
HUMUS
=====

Humus is a tool to periodically backup chunks of data (e.g. database backups) to Amazon's S3.  Humus' features include:

* CLI tool and Python library.
* Automatic file rotation
* Automatic date based file trimming.

Why another S3 backup tool?
===========================

Most of the backup tools out there were either foucused on backing up entire directories of files or didn't provide the rotation/trim tools I was looking for.


Installation & Use
==================

1. Run ``pip install humus``.
2. Create a config file like the following at ``./humus.ini``, ``~/humus.ini``, ``/etc/humus.ini``, or ``/etc/humus/humus.ini``::

    [AWS]
    access_key=< YOUR AWS ACCESS KEY >
    secret_key=< YOUR AWS SECRET KEY >
    bucket=some-bucket-name

    # Everything after this point is optional
    path=backups

    [humus]
    # The number of files to exist in the S3 directory before getting trimmed
    count_limit=2
    # The age in days where files should be trimmed
    age_limit=2
    # The chunk size in bytes for data to be passed to bz2
    chunk_size=1024

    # Leave out this section if you want your backup to be unencrypted.
    [encryption]
    gpg_binary=gpg
    encrypt_command=%(gpg_command)s -c --no-use-agent --batch --yes --passphrase %(passphrase)s --cipher-algo AES256 -o %(output_file)s %(input_file)s
    passphrase=< YOUR REALLY LONG ENCRYPTION PASSPHRASE >

3. Run the command ``humus my_filename target_file`` or ``output_cmd | humus my_filename`` whenever you want to make a new backup.

Restoring Backups
=================

To restore a backup, simply download the saved file from S3 using your client of choice.

If you used the encryption options above, you can decrypt your backup using the following command::

    gpg -c --no-use-agent --batch --yes --passphrase < YOUR REALLY LONG ENCRYPTION PASSPHRASE > --cipher-algo AES256 -o my_file.bz2 my_encrypted_file.bz2
