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

COMMENT ON VIEW HostGuestsReport
  IS 'List all systems, along with their guests';

COMMENT ON COLUMN HostGuestsReport.mgm_id
  IS 'The id of the SUSE Manager instance that contains this data';
COMMENT ON COLUMN HostGuestsReport.host
  IS 'The id of the host system';
COMMENT ON COLUMN HostGuestsReport.guest
  IS 'The id of the guest system';
COMMENT ON COLUMN HostGuestsReport.synced_date
  IS 'The timestamp of when this data was last refreshed.';
