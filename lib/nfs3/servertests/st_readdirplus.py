from nfs3.nfs3_const import *
from environment import check, homedir_fh
from nfs3.nfs3lib import *

def testNfs3ReadDirPlus(t, env):
    """ Retrieve entries sequentially from a dir via the READDIRPLUS rpc 
    
    
    FLAGS: nfsv3 readdirplus all
    DEPEND: 
    CODE: RDDIRPLS1
    #ToDo:  switch depend to create1 once bug #76982 is closed
    """
    ### Setup Phase ###
    test_file=t.name + "_file_1"
    created_files=[]
    test_dir=t.name + "_dir_1"
    mnt_fh = homedir_fh(env.mc, env.c1)
    cookie = 0
    cookie_verf = 0
    dir_count = 150
    max_count = 1200
    test_file_count = 15
    
    res = env.c1.mkdir(mnt_fh, test_dir, dir_mode_set=1, dir_mode_val=0777)
    check(res, msg="MKDIR - dir %s" % test_dir)
    test_dir_fh = res.resok.obj.handle.data
    
    for i in range(1, test_file_count + 1):
        temp_name = "%s_%s" % (test_file, i)
        res = env.c1.create(test_dir_fh, temp_name, file_mode_set=1, 
            file_mode_val=0777)
        check(res, msg="CREATE - file %s" % temp_name)
        created_files.append(temp_name)
        
    ### Execution Phase ###
    entries = env.c1.do_readdirplus(test_dir_fh, cookie, cookie_verf, dir_count, max_count)
        
    ### Verification Phase ###
    # Add 2 to the count to account for "." and ".." entries
    if len(entries) != test_file_count + 2:
        t.fail_support(" ".join([
            "READDIR - number of dir entries returned [%s]" % len(entries), 
            "does not match number created [%s]" % (test_file_count + 2)]))
    for e in entries:
        if e.name not in created_files:
            if e.name != "." and e.name != "..":
                t.fail_support(" ".join([
                    "READDIR - returned entry name [%s]" % e.name,
                    "was not in the list of created files [%s]" %\
                        ("\n".join(created_files))
                    ]))


### Variations:
# NFS3ERR_BAD_COOKIE detection and handling?
# size = 0 --> NFS3ERR_TOOSMALL
# verify the returned attributes againts a single read call
# dirsize > maxsize
