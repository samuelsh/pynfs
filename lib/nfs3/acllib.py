#!/usr/bin/env python
# acllib.py - POSIX ACL library for python

import rpc
from xdrlib import Error as XDRError
from acl_const import *
from acl_type import *
from acl_pack import *
from nfs3_const import *
from nfs3_type import *
from nfs3_pack import *

AuthSys = rpc.SecAuthSys(0, 'jupiter', 103558, 100, [])


class ACLException(rpc.RPCError):
    pass


# An ACL procedure returned an error
class BadACLRes(ACLException):
    def __init__(self, errcode, msg=None):
        self.errcode = errcode
        if msg:
            self.msg = msg + ': '
        else:
            self.msg = ''

    def __str__(self):
        return self.msg + "should return ACL3_OK, instead got %s" % \
               (nfsstat3[self.errcode])


class ACLClient(rpc.RPCClient):
    def __init__(self, id, host='localhost', port=300, homedir=['pynfs'],
                 sec_list=[AuthSys], opts=None, acl_version=NFS_ACL_V3):
        self.ipv6 = getattr(opts, 'ipv6', False)
        self.packer = ACLPacker()
        self.unpacker = ACLUnpacker('')
        self.homedir = homedir
        self.id = id
        self.opts = opts
        uselowport = getattr(opts, "secure", False)
        rpc.RPCClient.__init__(self, host, port, program=NFS_ACL_PROGRAM,
                               version=acl_version, sec_list=sec_list,
                               uselowport=uselowport, ipv6=self.ipv6)
        self.server_address = (host, port)
        print "seclist = ", sec_list

    def acl_pack_v3(self, procedure, data):
        p = self.packer

        if procedure == ACLPROC3_NULL:
            pass
        elif procedure == ACLPROC3_GETACL:
            p.pack_GETACL3args(data)
        elif procedure == ACLPROC3_SETACL:
            p.pack_SETACL3args(data)
        elif procedure == ACLPROC3_GETXATTRDIR:
            p.pack_GETXATTRDIR3args(data)
        else:
            # raise XDRError, 'bad switch=%s' % procedure
            print("XDRError: bad switch=%s" % procedure)

    # XXX Fancy unpacking, into status, data, etc
    def acl_unpack_v3(self, procedure):
        un_p = self.unpacker
        if procedure == ACLPROC3_NULL:
            pass
        elif procedure == ACLPROC3_GETACL:
            return un_p.unpack_GETACL3res()
        elif procedure == ACLPROC3_SETACL:
            return un_p.unpack_SETACL3res()
        elif procedure == ACLPROC3_GETXATTRDIR:
            return un_p.unpack_GETXATTRDIR3res()
        else:
            # raise XDRError, 'bad switch=%s' % procedure
            print("XDRError: bad switch=%s" % procedure)

    def acl_pack_v2(self, procedure, data):
        p = self.packer

        if procedure == ACLPROC2_NULL:
            pass
        elif procedure == ACLPROC2_GETACL:
            p.pack_GETACL2args(data)
        elif procedure == ACLPROC2_SETACL:
            p.pack_SETACL2args(data)
        elif procedure == ACLPROC2_GETATTR:
            p.pack_GETATTR2args(data)
        elif procedure == ACLPROC2_ACCESS:
            p.pack_ACCESS2args(data)
        elif procedure == ACLPROC2_GETXATTRDIR:
            p.pack_GETXATTRDIR2args(data)
        else:
            raise XDRError, 'bad switch=%s' % procedure

    # XXX Fancy unpacking, into status, data, etc
    def acl_unpack_v2(self, procedure):
        un_p = self.unpacker
        if procedure == ACLPROC2_NULL:
            pass
        elif procedure == ACLPROC2_GETACL:
            return un_p.unpack_GETACL2res()
        elif procedure == ACLPROC2_SETACL:
            return un_p.unpack_SETACL2res()
        elif procedure == ACLPROC2_GETATTR:
            return un_p.unpack_SETACL2res()
        elif procedure == ACLPROC2_ACCESS:
            return un_p.unpack_SETACL2res()
        elif procedure == ACLPROC2_GETXATTRDIR:
            return un_p.unpack_GETXATTRDIR2res()
        else:
            raise XDRError, 'bad switch=%s' % procedure

    def acl_pack_v4(self, procedure, data):
        p = self.packer

        if procedure == ACLPROC2_NULL:
            pass
        elif procedure == ACLPROC2_GETACL:
            p.pack_GETACL2args(data)
        elif procedure == ACLPROC2_SETACL:
            p.pack_SETACL2args(data)
        else:
            raise XDRError, 'bad switch=%s' % procedure

    # XXX Fancy unpacking, into status, data, etc
    def acl_unpack_v4(self, procedure):
        un_p = self.unpacker
        if procedure == ACLPROC2_NULL:
            pass
        elif procedure == ACLPROC2_GETACL:
            return un_p.unpack_GETACL2res()
        elif procedure == ACLPROC2_SETACL:
            return un_p.unpack_SETACL2res()
        else:
            raise XDRError, 'bad switch=%s' % procedure

    pack_to_version = {
        NFS_ACL_V2: acl_pack_v2,
        NFS_ACL_V3: acl_pack_v3,
        NFS_ACL_V4: acl_pack_v4
    }
    unpack_to_version = {
        NFS_ACL_V2: acl_unpack_v2,
        NFS_ACL_V3: acl_unpack_v3,
        NFS_ACL_V4: acl_unpack_v4
    }

    def acl_call(self, procedure, data='', acl_version=NFS_ACL_V3):
        # Pack Request
        p = self.packer
        un_p = self.unpacker
        p.reset()

        print("### DEBUG: acl_version={}".format(acl_version))
        self.pack_to_version[acl_version](self, procedure, data)

        # Make Call
        res = self.call(procedure, p.get_buffer())

        # Unpack Reply
        un_p.reset(res)
        res = self.unpack_to_version[acl_version](self, procedure)
        un_p.done()

        # XXX Error checking?
        return res

    """
    ACLV3 OPERATIONS (NFS3)
    """

    def acl_null(self):
        return self.acl_call(ACLPROC3_NULL)

    def acl_getacl(self, file_handle, mask=None):
        arg_list = GETACL3args(nfs_fh3(file_handle), mask)
        return self.acl_call(ACLPROC3_GETACL, arg_list)

    def acl_setacl(self, file_handle, acls, mask=0x0):
        """
         * This is the format of an ACL which is passed over the network.
        struct aclent {
            int type;
            uid id;
            o_mode perm;
        };
        """
        args_list = SETACL3args(nfs_fh3(file_handle), secattr(mask, len(acls), [aclent(*acl) for acl in acls], 0, []))
        return self.acl_call(ACLPROC3_SETACL, args_list)

    def acl_getxattrdir(self, file_handle, create=False):
        arg_list = GETXATTRDIR3args(nfs_fh3(file_handle), create)
        return self.acl_call(ACLPROC3_GETXATTRDIR, arg_list)

    def acl_all_programms(self, file_handle, proc):
        arg_list = GETXATTRDIR3args(nfs_fh3(file_handle), False)
        return self.acl_call(proc, arg_list)

    """
    ACLV2 OPERATIONS (NFS2)
    """

    def acl2_null(self):
        return self.acl_call(ACLPROC2_NULL, acl_version=NFS_ACL_V2)

    def acl2_getattr(self, file_handle):
        arg_list = GETATTR2args(nfs_fh(file_handle))
        return self.acl_call(ACLPROC2_GETATTR, arg_list, acl_version=NFS_ACL_V2)

    def acl2_access(self, file_handle, access):
        arg_list = ACCESS2args(nfs_fh(file_handle), access)
        return self.acl_call(ACLPROC2_ACCESS, arg_list, acl_version=NFS_ACL_V2)

    def acl2_getacl(self, file_handle, mask=None):
        arg_list = GETACL2args(nfs_fh(file_handle), mask)
        return self.acl_call(ACLPROC2_GETACL, arg_list, acl_version=NFS_ACL_V2)

    def acl2_setacl(self, file_handle, acls, mask=0x0):
        """
         * This is the format of an ACL which is passed over the network.
        struct aclent {
            int type;
            uid id;
            o_mode perm;
        };
        """
        args_list = SETACL2args(nfs_fh(file_handle), secattr(mask, len(acls), [aclent(*acl) for acl in acls], 0, []))
        return self.acl_call(ACLPROC2_SETACL, args_list, acl_version=NFS_ACL_V2)

    def acl2_getxattrdir(self, file_handle, create=False):
        arg_list = GETXATTRDIR2args(nfs_fh(file_handle), create)
        return self.acl_call(ACLPROC2_GETXATTRDIR, arg_list, acl_version=NFS_ACL_V2)

    """
    ACLV4 OPERATIONS (NFS4)
    """

    def acl4_null(self):
        return self.acl_call(ACLPROC4_NULL, acl_version=NFS_ACL_V2)

    def acl4_getacl(self, file_handle, mask=None):
        arg_list = GETACL4args(nfs_fh4(file_handle), mask)
        return self.acl_call(ACLPROC4_GETACL, arg_list, acl_version=NFS_ACL_V2)

    def acl4_setacl(self, file_handle, acls, mask=0x0):
        """
         * This is the format of an ACL which is passed over the network.
        struct aclent {
            int type;
            uid id;
            o_mode perm;
        };
        """
        args_list = SETACL4args(nfs_fh4(file_handle), secattr(mask, len(acls), [aclent(*acl) for acl in acls], 0, []))
        return self.acl_call(ACLPROC4_SETACL, args_list, acl_version=NFS_ACL_V2)

    """
    UTILITY FUNCTIONS
    """

    # Verify if ACL call was successful,
    # raise BadACLRes otherwise
    def acl_check_result(self, res, msg=None):
        if not res.status:
            return
        raise BadACLRes(res.status, msg)
