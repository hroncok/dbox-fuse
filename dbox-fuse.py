#!/usr/bin/env python
import os, stat, errno, locale, time
import fuse
from fuse import Fuse
from dropbox import client, rest, session
from memoized import *

if not hasattr(fuse, '__version__'):
    raise RuntimeError, \
        '''your fuse-py doesn't know of fuse.__version__, probably it's too old.'''

fuse.fuse_python_api = (0, 2)

version = '0.0.1'

from _login import *
#APP_KEY = 'foo'
#APP_SECRET = 'bar'

TOKEN_FILE = os.path.expanduser('~/.dbox-fuse-token')

class StoredSession(session.DropboxSession):
    '''a wrapper around DropboxSession that stores a token to a file on disk'''
    def load_creds(self):
        try:
            stored_creds = open(TOKEN_FILE).read()
            self.set_token(*stored_creds.split('|'))
        except IOError:
            pass # don't worry if it's not there

    def write_creds(self, token):
        f = open(TOKEN_FILE, 'w')
        f.write('|'.join([token.key, token.secret]))
        f.close()

    def delete_creds(self):
        os.unlink(TOKEN_FILE)

    def link(self):
        request_token = self.obtain_request_token()
        url = self.build_authorize_url(request_token)
        print('url: '+url)
        print('Please authorize in the browser. After you\'re done, press enter.')
        raw_input()

        self.obtain_access_token(request_token)
        self.write_creds(self.token)

    def unlink(self):
        self.delete_creds()
        session.DropboxSession.unlink(self)

class FileStat(fuse.Stat):
    def __init__(self):
        self.st_mode = 0
        self.st_ino = 0
        self.st_dev = 0
        self.st_nlink = 0
        self.st_uid = 0
        self.st_gid = 0
        self.st_size = 0
        self.st_atime = 0
        self.st_mtime = 0
        self.st_ctime = 0

class DboxFuse(Fuse):
    def __init__(self, *args, **kw):
        Fuse.__init__(self, *args, **kw)
        self.sess = StoredSession(APP_KEY, APP_SECRET, access_type='dropbox')
        self.api_client = client.DropboxClient(self.sess)
        self.sess.load_creds()
        if not self.sess.is_linked():
            try:
                self.sess.link()
            except rest.ErrorResponse, e:
                print('Error: '+e)
                exit(1)

    @memoized
    def getattr(self, path):
        st = FileStat()
        if path == '/':
            st.st_mode = stat.S_IFDIR | 0755
            st.st_nlink = 2
        else:
            try:
                resp = self.api_client.metadata(path,list=False)
            except rest.ErrorResponse:
                return st
            if resp['is_dir']:
                st.st_mode = stat.S_IFDIR | 0755
                st.st_nlink = 2
            else:
                st.st_mode = stat.S_IFREG | 0644
                st.st_nlink = 1
                st.st_size = resp['bytes']
                st.st_mtime = self.st_atime = self.st_ctime = float(time.strftime('%s',time.strptime(resp['modified'][5:-6],'%d %b %Y %H:%M:%S')))
        return st

    @memoyield
    def readdir(self, path, offset):
        resp = self.api_client.metadata(path)
        if 'contents' in resp:
            for f in resp['contents'] + [{'path': '.'}, {'path': '..'}]:
                name = os.path.basename(f['path'])
                encoding = locale.getdefaultlocale()[1]
                yield fuse.Direntry(name.encode(encoding))

    def read(self, path, size, offset):
        f = self.api_client.get_file(path)
        return f.read()[offset:offset+size]

if __name__ == '__main__':
    usage='''
Dropbox fuse mount

''' + Fuse.fusage
    try:
        server = DboxFuse(version='%prog ' + version,
                         usage=usage,
                         dash_s_do='setsingle')

        server.parse(errex=1)
        server.main()
    except fuse.FuseError:
        pass
