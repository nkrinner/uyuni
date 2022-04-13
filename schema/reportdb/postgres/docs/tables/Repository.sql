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

COMMENT ON TABLE Repository
  IS 'The list of repositories managed by a SUSE Manager instance';

COMMENT ON COLUMN Repository.mgm_id
  IS 'The id of the SUSE Manager instance that contains this data';
COMMENT ON COLUMN Repository.repository_id
  IS 'The id of the repository';
COMMENT ON COLUMN Repository.label
  IS 'The unique label of the repository';
COMMENT ON COLUMN Repository.url
  IS 'The url where the repository is reachable';
COMMENT ON COLUMN Repository.type
  IS 'The type of the repository. Possible values: yum, uln, deb';
COMMENT ON COLUMN Repository.metadata_signed
  IS 'True if the metadata of this repositories is signed';
COMMENT ON COLUMN Repository.organization
  IS 'The organization that owns this data';
COMMENT ON COLUMN Repository.synced_date
  IS 'The timestamp of when this data was last refreshed.';
