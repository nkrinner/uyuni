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

COMMENT ON VIEW SystemGroupsSystemsReport
  IS 'List of all systems which belongs to any system group';

COMMENT ON COLUMN SystemGroupsSystemsReport.mgm_id
  IS 'The id of the SUSE Manager instance that contains this data';
COMMENT ON COLUMN SystemGroupsSystemsReport.group_id
  IS 'The id of this system group';
COMMENT ON COLUMN SystemGroupsSystemsReport.group_name
  IS 'The unique name of this system group';
COMMENT ON COLUMN SystemGroupsSystemsReport.system_id
  IS 'The id of the system';
COMMENT ON COLUMN SystemGroupsSystemsReport.system_name
  IS 'The unique descriptive name of the system';
COMMENT ON COLUMN SystemGroupsSystemsReport.synced_date
  IS 'The timestamp of when this data was last refreshed.';
