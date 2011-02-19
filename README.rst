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