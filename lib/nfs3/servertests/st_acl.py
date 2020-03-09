from nfs3.nfs3_const import *
from nfs3.acl_const import *
from environment import check, checkvalid, homedir_fh
from nfs3.nfs3lib import *


def testNfs3ACL_BasicACLv3Operations(t, env):
    """ Create a file with all _set bits = 0
        Failure is expected due to bug #76982

    FLAGS: nfsv3 acl all
    DEPEND:
    CODE: GETACL01
    """
    ### Setup Phase ###
    test_file = b"_file_1"
    test_dir = t.name + "_dir_1"
    mnt_fh = homedir_fh(env.mc, env.c1)

    res = env.c1.mkdir(mnt_fh, test_dir, dir_mode_set=1, dir_mode_val=0777)
    check(res, msg="MKDIR - test dir %s" % test_dir)
    test_dir_fh = res.resok.obj.handle.data

    ### Execution Phase ###
    res = env.c1.create(test_dir_fh, test_file, file_mode_set=0,
                        file_mode_val=0777)
    test_file_fh = res.resok.obj.handle.data

    ### Verification Phase ###
    check(res, msg="CREATE - file %s" % test_file)
    res = env.c1.lookup(test_dir_fh, test_file)
    check(res, msg="LOOKUP - file %s" % test_file)
    env.acl_c3.acl_null()
    env.acl_c3.acl_setacl(test_file_fh, [(0x1, 1000, 0o777), (0x2, 2000, 0o777), (0x3, 0, 0o777)],
                          mask=0x0)
    res = env.acl_c3.acl_getacl(test_file_fh, 0x1)
    print "###DEBUG - GETACL3 RESULTS:", res, "\n"
    try:
        res = env.acl_c3.acl_getxattrdir(test_file_fh, True)
    except Exception as e:
        print("{}".format(e))
