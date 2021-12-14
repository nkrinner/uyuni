/*
 * Copyright (c) 2014 Red Hat, Inc.
 *
 * This software is licensed to you under the GNU General Public License,
 * version 2 (GPLv2). There is NO WARRANTY for this software, express or
 * implied, including the implied warranties of MERCHANTABILITY or FITNESS
 * FOR A PARTICULAR PURPOSE. You should have received a copy of GPLv2
 * along with this software; if not, see
 * http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.
 *
 * Red Hat trademarks are not licensed under GPLv2. No permission is
 * granted to use or replicate Red Hat trademarks that are incorporated
 * in this software or its documentation.
 */
package com.redhat.rhn.frontend.action.multiorg;

import com.redhat.rhn.domain.org.usergroup.UserGroupFactory;
import com.redhat.rhn.domain.user.User;
import com.redhat.rhn.frontend.struts.RequestContext;
import com.redhat.rhn.frontend.struts.RhnAction;
import com.redhat.rhn.frontend.taglibs.list.helper.ListSessionSetHelper;
import com.redhat.rhn.frontend.taglibs.list.helper.Listable;

import org.apache.struts.action.ActionForm;
import org.apache.struts.action.ActionForward;
import org.apache.struts.action.ActionMapping;
import org.apache.struts.action.DynaActionForm;

import java.util.List;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;


/**
 * ExtAuthRoleMappingAction
 */
public class ExtAuthRoleMappingAction extends RhnAction implements Listable {

    /** {@inheritDoc} */
    @Override
    public ActionForward execute(ActionMapping mapping, ActionForm formIn,
            HttpServletRequest request, HttpServletResponse response) {
        DynaActionForm daForm = (DynaActionForm) formIn;

        ListSessionSetHelper helper = new ListSessionSetHelper(this, request);
        helper.execute();
        return mapping.findForward("default");
    }

    /**
     * ${@inheritDoc}
     */
    public List getResult(RequestContext contextIn) {
        User user = contextIn.getCurrentUser();
        return UserGroupFactory.listExtAuthGroups(user);
    }

}
