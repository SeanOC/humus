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
    path=bacups

    [humus]
    # The number of files to exist in the S3 directory before getting trimmed
    count_limit=2
    # The age in days where files should be trimmed
    age_limit=2
    # The chunk size in bytes for data to be passed to bz2
    chunk_size=1024

3. Run the command ``humus my_filename target_file`` or ``output_cmd | humus my_filename`` whenever you want to make a new backup.
