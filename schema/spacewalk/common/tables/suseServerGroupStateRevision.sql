--
-- Copyright (c) 2016 SUSE LLC
--
-- This software is licensed to you under the GNU General Public License,
-- version 2 (GPLv2). There is NO WARRANTY for this software, express or
-- implied, including the implied warranties of MERCHANTABILITY or FITNESS
-- FOR A PARTICULAR PURPOSE. You should have received a copy of GPLv2
-- along with this software; if not, see
-- http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.
--
-- Red Hat trademarks are not licensed under GPLv2. No permission is
-- granted to use or replicate Red Hat trademarks that are incorporated
-- in this software or its documentation.
--

CREATE TABLE suseServerGroupStateRevision
(
    group_id         NUMERIC NOT NULL
                          CONSTRAINT suse_server_group_gr_id_fk
                              REFERENCES rhnServerGroup (id)
                              ON DELETE CASCADE,
    state_revision_id NUMERIC NOT NULL
                          CONSTRAINT suse_server_group_sr_id_fk
                              REFERENCES suseStateRevision (id)
                              ON DELETE CASCADE
)

;

ALTER TABLE suseServerGroupStateRevision
    ADD CONSTRAINT suse_server_group_rev_grid_uq UNIQUE (group_id, state_revision_id);
