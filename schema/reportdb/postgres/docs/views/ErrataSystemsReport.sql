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

COMMENT ON VIEW ErrataSystemsReport
  IS 'Patches out of compliance information with the details about the system.';

COMMENT ON COLUMN ErrataSystemsReport.mgm_id
  IS 'The id of the SUSE Manager instance that contains this data';
COMMENT ON COLUMN ErrataSystemsReport.errata_id
  IS 'The id of the patch';
COMMENT ON COLUMN ErrataSystemsReport.advisory_name
  IS 'The unique name of this advisory';
COMMENT ON COLUMN ErrataSystemsReport.system_id
  IS 'The id of the system';
COMMENT ON COLUMN ErrataSystemsReport.profile_name
  IS 'The unique descriptive name of the system';
COMMENT ON COLUMN ErrataSystemsReport.hostname
  IS 'The hostname that identifies this system';
COMMENT ON COLUMN ErrataSystemsReport.ip_address
  IS 'The IPv4 address of the primary network interface of the system';
COMMENT ON COLUMN ErrataSystemsReport.ip6_addresses
  IS 'The list of IPv6 addresses and their scopes of the primary network interface of the system, separated by ;';
COMMENT ON COLUMN ErrataSystemsReport.synced_date
  IS 'The timestamp of when this data was last refreshed.';
