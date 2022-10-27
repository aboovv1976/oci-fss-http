from pyNfsClient import (Portmap, Mount, NFSv3, MNT3_OK, NFS_PROGRAM, NFS_V3, NFS3_OK, DATA_SYNC)
import sys
import os

# The NfsClient class is a holder to call NFS calls.
# See https://pypi.org/project/pyNfsClient/
# Add pyNfsClient in your requirements.txt file when building Functions or containers
TIMEOUT=5
class NfsClient():
    def __init__(self,hostname='fssClient',uid=0,gid=0,gids=[]):
        self.uid=uid
        self.gid=gid
        self.gids=gids
        self.mount=self.nfs3=None
        self.auth = {
                "flavor": 1,
                "machine_name": "host1",
                "uid": 0,
                "gid": 0,
                "aux_gid": gids
        }
        # -1 not connected
        # 0 - connected
        # 1 - Transport Error
        self.status=-1

    def connect(self,host):
        self.host=host
        self.portmap = Portmap(host, timeout=TIMEOUT)
        # The source bind port is less than 1023 and hence this should be executed as root
        # if unpriv ports are needed, modify rpc.py in the pyNfsClient module.
        try:
            self.portmap.connect()
            mnt_port = self.portmap.getport(Mount.program, Mount.program_version)
            self.mount = Mount(host=host, port=mnt_port, timeout=TIMEOUT, auth=self.auth)
            self.mount.connect()
            nfs_port =self.portmap.getport(NFS_PROGRAM, NFS_V3)
            self.nfs3 =NFSv3(host=host, port=nfs_port, timeout=TIMEOUT,auth=self.auth)
            self.nfs3.connect()
            self.status=0
        except:
            self.status=1
        return self.status

    def lookup(self,path):
        comp=path.split("/")
        dir='/'.join(comp[:-1])
        if not self.mount or not self.nfs3 or self.status != 0:
            return None
        mnt_res=self.mount.mnt(dir, self.auth)
        if mnt_res["status"] == MNT3_OK:
            root_fh =mnt_res["mountinfo"]["fhandle"]
            lookup_res = self.nfs3.lookup(root_fh, comp[-1], self.auth)
            return lookup_res
        else:
            return mnt_res


c=NfsClient()
c.connect('10.32.1.200')
print(c.lookup("/fss-1/TEST"))
