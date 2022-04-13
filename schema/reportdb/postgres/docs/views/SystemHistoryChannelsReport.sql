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

COMMENT ON VIEW SystemHistoryChannelsReport
  IS 'Channel event history.';

COMMENT ON COLUMN SystemHistoryChannelsReport.mgm_id
  IS 'The id of the SUSE Manager instance that contains this data';
COMMENT ON COLUMN SystemHistoryChannelsReport.system_id
  IS 'The id of the system';
COMMENT ON COLUMN SystemHistoryChannelsReport.history_id
  IS 'The id of the history event';
COMMENT ON COLUMN SystemHistoryChannelsReport.event_time
  IS 'When this event has happened';
COMMENT ON COLUMN SystemHistoryChannelsReport.status
  IS 'The current status of the action. Possible values Queued, Picked Up, Completed, Failed';
COMMENT ON COLUMN SystemHistoryChannelsReport.event
  IS 'The type of history event';
COMMENT ON COLUMN SystemHistoryChannelsReport.event_data
  IS 'Additional information related to the event triggered by this action';
COMMENT ON COLUMN SystemHistoryChannelsReport.synced_date
  IS 'The timestamp of when this data was last refreshed.';
