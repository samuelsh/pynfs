from nfs3.nfs3_const import *
from environment import check, homedir_fh
from nfs3.nfs3lib import *

def testNfs3FSInfo(t, env):
    """Retrieve the information of a file via the FSINFO rpc 
    
    
    FLAGS: nfsv3 fsinfo all
    DEPEND: 
    CODE: FSINFO1
    """
    ### Setup Phase ###
    test_file=t.name + "_file_1"
    test_dir=t.name + "_dir_1"
    mnt_fh = homedir_fh(env.mc, env.c1)
    
    res = env.c1.mkdir(mnt_fh, test_dir, dir_mode_set=1, dir_mode_val=0777)
    check(res, msg="MKDIR - dir %s" % test_dir)
    test_dir_fh = res.resok.obj.handle.data
    res = env.c1.create(test_dir_fh, test_file, file_mode_set=1, 
                        file_mode_val=0777)
    check(res, msg="CREATE - file %s" % test_file)
    test_file_fh = res.resok.obj.handle.data
    
    ### Execution Phase ###
    res = env.c1.fsinfo(test_file_fh)

    ### Verification Phase ###s
    check(res, msg="FSINFO - file %s" % test_file)

### Variations:
#    Dir
#    Different file types (nodes, symlinks, links, etc)
#    No Read/lookup/search Permission
#    Different permissions
