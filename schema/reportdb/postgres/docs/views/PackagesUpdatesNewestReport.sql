--
-- Copyright (c) 2022 SUSE LLC
--
-- This software is licensed to you under the GNU General Public License,
-- version 2 (GPLv2). There is NO WARRANTY for this software, express or
-- implied, including the implied warranties of MERCHANTABILITY or FITNESS
-- FOR A PARTICULAR PURPOSE. You should have received a copy of GPLv2
-- along with this software; if not, see
-- http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.
--

COMMENT ON VIEW PackagesUpdatesNewestReport
  IS 'List of packages that can be updated for all systems, showing only the newest package version available.';

COMMENT ON COLUMN PackagesUpdatesNewestReport.mgm_id
  IS 'The id of the SUSE Manager instance that contains this data';
COMMENT ON COLUMN PackagesUpdatesNewestReport.system_id
  IS 'The id of the system';
COMMENT ON COLUMN PackagesUpdatesNewestReport.organization
  IS 'The organization that owns this data';
COMMENT ON COLUMN PackagesUpdatesNewestReport.package_name
  IS 'The name of the package';
COMMENT ON COLUMN PackagesUpdatesNewestReport.package_epoch
  IS 'The epoch of the installed package';
COMMENT ON COLUMN PackagesUpdatesNewestReport.package_version
  IS 'The version number of the installed package';
COMMENT ON COLUMN PackagesUpdatesNewestReport.package_release
  IS 'The release number of the installed package';
COMMENT ON COLUMN PackagesUpdatesNewestReport.package_arch
  IS 'The architecture of the package installed package';
COMMENT ON COLUMN PackagesUpdatesNewestReport.newer_epoch
  IS 'The epoch of the new package that can be installed';
COMMENT ON COLUMN PackagesUpdatesNewestReport.newer_version
  IS 'The version number of the new package that can be installed';
COMMENT ON COLUMN PackagesUpdatesNewestReport.newer_release
  IS 'The release number of the new package that can be installed';
COMMENT ON COLUMN PackagesUpdatesNewestReport.synced_date
  IS 'The timestamp of when this data was last refreshed.';
