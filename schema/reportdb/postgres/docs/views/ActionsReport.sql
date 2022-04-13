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

COMMENT ON VIEW ActionsReport
  IS 'List of all actions performed on all systems';

COMMENT ON COLUMN ActionsReport.mgm_id
  IS 'The id of the SUSE Manager instance that contains this data';
COMMENT ON COLUMN ActionsReport.action_id
  IS 'The id of the action';
COMMENT ON COLUMN ActionsReport.earliest_action
  IS 'The earliest time the action was schedule for execution';
COMMENT ON COLUMN ActionsReport.event
  IS 'The type of event triggered by the action';
COMMENT ON COLUMN ActionsReport.action_name
  IS 'The name of the action';
COMMENT ON COLUMN ActionsReport.scheduler_id
  IS 'The id of the account who scheduled the action';
COMMENT ON COLUMN ActionsReport.scheduler_username
  IS 'The username of the account who scheduled the action';
COMMENT ON COLUMN ActionsReport.in_progress_systems
  IS 'Number of system where the action is still in progress';
COMMENT ON COLUMN ActionsReport.completed_systems
  IS 'Number of system where the action is completed';
COMMENT ON COLUMN ActionsReport.failed_systems
  IS 'Number of system where the action is failed';
COMMENT ON COLUMN ActionsReport.archived
  IS 'True if the action is archived';
COMMENT ON COLUMN ActionsReport.synced_date
  IS 'The timestamp of when this data was last refreshed.';
