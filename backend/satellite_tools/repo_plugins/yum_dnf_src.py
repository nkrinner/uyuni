#
# Copyright (c) 2008--2011 Red Hat, Inc.
# Copyright (c) 2010--2011 SUSE LINUX Products GmbH, Nuernberg, Germany.
#
# This software is licensed to you under the GNU General Public License,
# version 2 (GPLv2). There is NO WARRANTY for this software, express or
# implied, including the implied warranties of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. You should have received a copy of GPLv2
# along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.
#
# Red Hat trademarks are not licensed under GPLv2. No permission is
# granted to use or replicate Red Hat trademarks that are incorporated
# in this software or its documentation.
#

import shutil
import sys
import gzip
import os.path

import yum
from yum.config import ConfigParser
from yum.update_md import UpdateMetadata, UpdateNoticeException, UpdateNotice
from yum.yumRepo import YumRepository
try:
    from yum.misc import cElementTree_iterparse as iterparse
except ImportError:
    try:
        from xml.etree import cElementTree
    except ImportError:
        import cElementTree
    iterparse = cElementTree.iterparse
from spacewalk.satellite_tools.reposync import ContentPackage
from spacewalk.common.rhnConfig import CFG, initCFG

YUMSRC_CONF='/etc/rhn/spacewalk-repo-sync/yum.conf'

class YumWarnings:
    def write(self, s):
        pass
    def disable(self):
        self.saved_stdout = sys.stdout
        sys.stdout = self
    def restore(self):
        sys.stdout = self.saved_stdout

class YumUpdateMetadata(UpdateMetadata):
    """The root update metadata object supports getting all updates"""

    def add(self, obj, mdtype='updateinfo', all=False):
        """ Parse a metadata from a given YumRepository, file, or filename. """
        if not obj:
            raise UpdateNoticeException
        if type(obj) in (type(''), type(u'')):
            infile = obj.endswith('.gz') and gzip.open(obj) or open(obj, 'rt')
        elif isinstance(obj, YumRepository):
            if obj.id not in self._repos:
                self._repos.append(obj.id)
                md = obj.retrieveMD(mdtype)
                if not md:
                    raise UpdateNoticeException()
                infile = gzip.open(md)
        else:   # obj is a file object
            infile = obj

        for event, elem in iterparse(infile):
            if elem.tag == 'update':
                un = UpdateNotice(elem)
                key = un['update_id']
                if all:
                    key = "%s-%s" % (un['update_id'], un['version'])
                if not self._notices.has_key(key):
                    self._notices[key] = un
                    for pkg in un['pkglist']:
                        for file in pkg['packages']:
                            self._cache['%s-%s-%s' % (file['name'],
                                                      file['version'],
                                                      file['release'])] = un
                            no = self._no_cache.setdefault(file['name'], set())
                            no.add(un)

class ContentSource:
    repo = None
    cache_dir = '/var/cache/rhn/reposync/'
    def __init__(self, url, name):
        self.yumbase = yum.YumBase()
        self.yumbase.preconf.fn=YUMSRC_CONF
        if not os.path.exists(YUMSRC_CONF):
            self.yumbase.preconf.fn='/dev/null'
        self.configparser = ConfigParser()
        self._clean_cache(self.cache_dir + name)

        # read the proxy configuration in /etc/rhn/rhn.conf
        initCFG('server.satellite')
        self.proxy_addr = CFG.http_proxy
        self.proxy_user = CFG.http_proxy_username
        self.proxy_pass = CFG.http_proxy_password

        if (self.proxy_user is not None and self.proxy_pass is not None and self.proxy_addr is not None):
            self.proxy_url = "http://%s:%s@%s" %(self.proxy_user, self.proxy_pass, self.proxy_addr)
        elif (self.proxy_addr is not None):
            self.proxy_url = "http://%s" %(self.proxy_addr)
        else:
            self.proxy_url = None
        repo = yum.yumRepo.YumRepository(name)
        repo.populate(self.configparser, name, self.yumbase.conf)
        self.repo = repo
        repo.cache = 0
        repo.metadata_expire = 0
        repo.mirrorlist = url
        repo.baseurl = [url]
        repo.basecachedir = self.cache_dir
        repo.pkgdir = os.path.join(CFG.MOUNT_POINT, CFG.PREPENDED_DIR, '1')
        if hasattr(repo, 'base_persistdir'):
            repo.base_persistdir = self.cache_dir
        if self.proxy_url is not None:
            repo.proxy = self.proxy_url

        warnings = YumWarnings()
        warnings.disable()
        repo.baseurlSetup()
        warnings.restore()

        repo.setup(False)
        self.num_packages = 0
        self.num_excluded = 0


    def list_packages(self, filters):
        """ list packages"""
        sack = self.repo.getPackageSack()
        sack.populate(self.repo, 'metadata', None, 0)
        list = sack.returnPackages()
        self.num_packages = len(list)
        if filters:
            list = self._filter_packages(list, filters)
            list = self._get_package_dependencies(sack, list)
            self.num_excluded = self.num_packages - len(list)
        to_return = []
        for pack in list:
            if pack.arch == 'src':
                continue
            new_pack = ContentPackage()
            new_pack.setNVREA(pack.name, pack.version, pack.release, 
                              pack.epoch, pack.arch)
            new_pack.unique_id = pack
            new_pack.checksum_type = pack.checksums[0][0]
            if new_pack.checksum_type == 'sha':
                new_pack.checksum_type = 'sha1'
            new_pack.checksum      = pack.checksums[0][1]
            to_return.append(new_pack)
        return to_return

    def _filter_packages(self, packages, filters):
        """ implement include / exclude logic
            filters are: [ ('+', includelist1), ('-', excludelist1),
                           ('+', includelist2), ... ]
        """
        if filters is None:
            return

        selected = []
        excluded = []
        if filters[0][0] == '-':
            # first filter is exclude, start with full package list
            # and then exclude from it
            selected = packages
        else:
            excluded = packages

        for filter in filters:
            sense, pkg_list = filter
            if sense == '+':
                # include
                exactmatch, matched, unmatched = yum.packages.parsePackages(
                                                        excluded, pkg_list)
                allmatched = yum.misc.unique(exactmatch + matched)
                selected = yum.misc.unique(selected + allmatched)
                for pkg in allmatched:
                    if pkg in excluded:
                        excluded.remove(pkg)
            elif sense == '-':
                # exclude
                exactmatch, matched, unmatched = yum.packages.parsePackages(
                                                        selected, pkg_list)
                allmatched = yum.misc.unique(exactmatch + matched)
                for pkg in allmatched:
                    if pkg in selected:
                        selected.remove(pkg)
                excluded = yum.misc.unique(excluded + allmatched)
            else:
                raise UpdateNoticeException
        return selected

    def _get_package_dependencies(self, sack, packages):
        self.yumbase.pkgSack = sack
        resolved_deps = self.yumbase.findDeps(packages)
        for (pkg,deps) in resolved_deps.items():
            for (dep,dep_packages) in deps.items():
                packages.extend(dep_packages)
        return yum.misc.unique(packages)

    def get_package(self, package):
        """ get package """
        check = (self.verify_pkg, (package.unique_id ,1), {})
        return self.repo.getPackage(package.unique_id, checkfunc=check)

    def verify_pkg(self, fo, pkg, fail):
        return pkg.verifyLocalPkg()

    def _clean_cache(self, directory):
        shutil.rmtree(directory, True)

    def get_updates(self):
      if not self.repo.repoXML.repoData.has_key('updateinfo'):
        return []
      um = YumUpdateMetadata()
      um.add(self.repo, all=True)
      return um.notices
