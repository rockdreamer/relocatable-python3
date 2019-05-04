from __future__ import print_function
import os
import subprocess
from os import path
import glob
import shutil

def _execute(cmd, env):
    process = subprocess.Popen(cmd.split(), env=env)
    return process.wait()

def openssl_pre_make(options, buildout, environ):
    _execute(r'ms\do_ms.bat', environ)

def openssl_pre_make64(options, buildout, environ):
    _execute(r'ms\do_win64a.bat', environ)

def _xz_post_make(environ, platform):
    prefix = environ['PREFIX'].replace(os.path.sep, '/')
    os.system('cp -fvr include/* %s/include' % prefix)
    os.system('cp -fvr bin_%s/*a %s/lib' % (platform, prefix))
    os.system('cp -fvr bin_%s/*dll %s/bin' % (platform, prefix))

def xz_post_make(options, buildout, environ):
    _xz_post_make(environ, "i486")

def xz_post_make64(options, buildout, environ):
    _xz_post_make(environ, "x86-64")

def _db_post_make(platform_name, prefix):
    import os
    os.system('cp -fvr build_windows/*h %s/include' % prefix)
    os.system('cp -fvr build_windows/%s/Release/*lib %s/lib' % (platform_name, prefix))
    os.system('cp -fvr build_windows/%s/Release/*exe %s/bin' % (platform_name, prefix))

def db_post_make(options, buildout, environ):
    prefix = environ['PREFIX'].replace(os.path.sep, '/')
    _db_post_make('Win32', prefix)

def db_post_make64(options, buildout, environ):
    prefix = environ['PREFIX'].replace(os.path.sep, '/')
    _db_post_make('x64', prefix)

class PythonPostMake(object):
    def __init__(self, environ):
        from os import curdir
        self.python_source_path = path.abspath(path.join(curdir, path.pardir))
        self.pcbuild_path = path.join(self.python_source_path, 'PCbuild')
        self.prefix = environ['PREFIX']
        self.environ = environ
        print("%s %s %s" % (self.python_source_path, self.pcbuild_path, self.prefix))

    def make_install(self):
        self.move_libs()
        self.make_pyd()
        self.make_exe()
        self.make_dll()
        self.make_lib()
        self.make_ico()
        self.make_includes()
        self.make_libraries()
        self.move_dlls()
        self.copy_crt_assemblies()

    def move_dlls(self):
        dst = path.join(self.prefix, 'DLLs')
        src = glob.glob(path.join(self.prefix, 'bin', '*.dll'))
        _mk_path(dst)
        for item in src:
            if 'python35.dll' in item:
                continue
            cmd = 'mv %s %s' % (item, dst)
            _system(cmd)

    def move_libs(self):
        dst = path.join(self.prefix, 'libs')
        src = glob.glob(path.join(self.prefix, 'lib', '*.lib'))
        _mk_path(dst)
        for item in src:
            cmd = 'mv %s %s' % (item, dst)
            _system(cmd)

    def make_pyd(self):
        dst = path.join(self.prefix, 'DLLs')
        src = glob.glob(path.join(self.pcbuild_path, '*.pyd'))
        _copy_files(src, dst)

    def make_exe(self):
        dst = path.join(self.prefix, 'bin')
        src = glob.glob(path.join(self.pcbuild_path, '*.exe'))
        _copy_files(src, dst)

    def make_dll(self):
        dst = path.join(self.prefix, 'bin')
        src = glob.glob(path.join(self.pcbuild_path, '*.dll'))
        _copy_files(src, dst)

    def make_lib(self):
        dst = path.join(self.prefix, 'libs')
        src = glob.glob(path.join(self.pcbuild_path, '*.lib'))
        _copy_files(src, dst)

    def make_ico(self):
        dst = path.join(self.prefix, 'bin')
        src = glob.glob(path.join(self.pcbuild_path, '*.ico'))
        _copy_files(src, dst)

    def _copy_crt_assemblies(self, dst):
        os.makedirs(dst)
        src = glob.glob(path.join(self.environ['VC100CRT'], '*'))
        _copy_files(src, dst)

    def copy_crt_assemblies(self):
        dst = path.join(self.prefix, 'bin', 'Microsoft.VC100.CRT')
        self._copy_crt_assemblies(dst)
        dst = path.join(self.prefix, 'DLLs', 'Microsoft.VC100.CRT')
        self._copy_crt_assemblies(dst)

    def make_includes(self):
        import shutil
        cmd = "cp -fr %s %s" % (path.join(self.python_source_path, 'Include'),
                                path.join(self.prefix))
        _system(cmd)
        shutil.copy(path.join(self.python_source_path, 'PC', 'pyconfig.h'),
                     path.join(self.prefix, 'Include'))

    def make_libraries(self):
        dst = path.join(self.prefix,)
        src = path.join(self.python_source_path, 'lib')
        _mk_path(dst)
        cmd = "cp -fr %s %s" % (src, dst)
        _system(cmd)

def _mk_path(path):
    if os.path.exists(path):
        return
    os.makedirs(path)

def _copy_files(src_glob, dst):
    _mk_path(dst)
    for item in src_glob:
        print('cp %s %s' % (item, dst))
        shutil.copy(item, dst)

def _system(cmd):
    print(cmd)
    os.system(cmd.replace(os.path.sep, '/'))

def libevent_post_make(options, buildout, environ):
    import os
    prefix = environ['PREFIX'].replace(os.path.sep, '/')
    os.system('cp -fvr *lib %s/lib' % prefix)

def python_post_make(options, buildout, environ):
    instance = PythonPostMake(environ)
    instance.make_install()

def python_post_make64(options, buildout, environ):
    instance = PythonPostMake(environ)
    instance.make_install()
