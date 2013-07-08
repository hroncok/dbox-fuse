dbox-fuse - Mount Dropbox with fuse
===================================

If you want to mount Dropbox and not to synchronize, this is for you.

Status
------

This application is in very pre-alpha state. Use it at your own risk.

Currently, it only support browsing the file tree, reading some metadata and reading files. You cannot create or write anything yet.

Dependencies
------------

 * [python-dropbox](https://pypi.python.org/pypi/dropbox/1.6)
 * [fuse-python](https://sourceforge.net/apps/mediawiki/fuse/?title=FUSE_Python_tutorial) and fuse

Setup
-----

Go to [Dropbox app console](https://www.dropbox.com/developers/apps) and create an app. Select type **Core** and permission type **Full Dropbox**. Name it somehow and click **Create app**. Save **App key** and **App secret** to file `_login.py` in the same folder as `dbox-fuse.py`.

    APP_KEY = 'your_app_key_here'
    APP_SECRET = 'your_app_secret_here'

Create a directory, where you want to mount your Dropbox. Remember to do all actions as regular user, not as root!

    $ mkdir foo

Mount your Dropbox:

    $ ./dbox-fuse.py foo

Feel free to browse the folder. To umount , run:

    $ fusermount -zu foo

If something went wrong, you can force umount as root:

    # umount -l foo

License
-------

The app itself uses ISC license. However, it also uses other's code, see COPYING.
