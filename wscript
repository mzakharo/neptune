from waflib.Tools.compiler_c import c_compiler
c_compiler['win32'] = ['gcc']
def options(opt):
        opt.load('compiler_c')
def configure(cnf):
        cnf.load('compiler_c')
        cnf.env.append_value('INCLUDES', ['.'])


def build(bld):
    bld(features='c cprogram', source=bld.path.ant_glob('**/*.c'), target='ssocr', lib='imlib2')
