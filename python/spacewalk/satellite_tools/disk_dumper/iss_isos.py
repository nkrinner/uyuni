#  pylint: disable=missing-module-docstring
#
# Copyright (c) 2008--2015 Red Hat, Inc.
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

from spacewalk.satellite_tools import geniso


def create_isos(
    mountpoint,
    outdir,
    prefix,
    lower_limit=None,
    upper_limit=None,
    copy_iso_dir=None,
    iso_type=None,
):
    opts = [
        # pylint: disable-next=consider-using-f-string
        "--mountpoint=%s" % mountpoint,
        # pylint: disable-next=consider-using-f-string
        "--file-prefix=%s" % prefix,
        # pylint: disable-next=consider-using-f-string
        "--output=%s" % outdir,
        # pylint: disable-next=consider-using-f-string
        "--type=%s" % iso_type,
    ]

    if lower_limit is not None:
        # pylint: disable-next=consider-using-f-string
        opts.append("-v%s-%s" % (lower_limit, upper_limit))

    if copy_iso_dir is not None:
        # pylint: disable-next=consider-using-f-string
        opts.append("--copy-iso-dir=%s" % copy_iso_dir)

    geniso.main(opts)
