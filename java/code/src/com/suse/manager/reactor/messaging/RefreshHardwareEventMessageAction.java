package com.suse.manager.reactor.messaging;

import com.redhat.rhn.common.messaging.EventMessage;
import com.redhat.rhn.domain.action.Action;
import com.redhat.rhn.domain.action.ActionFactory;
import com.redhat.rhn.domain.action.server.ServerAction;
import com.redhat.rhn.domain.server.MinionServer;
import com.redhat.rhn.domain.server.MinionServerFactory;
import com.redhat.rhn.frontend.events.AbstractDatabaseAction;
import com.suse.manager.webui.services.SaltService;
import org.apache.log4j.Logger;

import java.util.Date;
import java.util.Optional;
import java.util.stream.Collectors;

/**
 * Created by matei on 3/28/16.
 */
public class RefreshHardwareEventMessageAction extends AbstractDatabaseAction {

    /* Logger for this class */
    private static final Logger LOG = Logger.getLogger(RefreshHardwareEventMessageAction.class);

    // Reference to the SaltService instance
    private final SaltService SALT_SERVICE;


    public RefreshHardwareEventMessageAction(SaltService saltService) {
        this.SALT_SERVICE = saltService;
    }

    @Override
    protected void doExecute(EventMessage msg) {
        RefreshHardwareEventMessage event = (RefreshHardwareEventMessage)msg;
        Action action = ActionFactory.lookupById(event.getActionId());
        if (action != null) {

            Optional<MinionServer> minionServerOpt = MinionServerFactory
                    .findByMinionId(event.getMinionId());

            minionServerOpt.ifPresent(minionServer -> {

                Optional<ServerAction> serverAction = action.getServerActions().stream()
                        .filter(sa -> sa.getServer().equals(minionServer)).findFirst();

                serverAction.ifPresent(sa -> {
                    LOG.debug("Refreshing hardware for: " + minionServer.getMinionId());

                    GetHardwareInfoEventMessageAction hardwareAction = new GetHardwareInfoEventMessageAction(SALT_SERVICE);
                    hardwareAction.execute(new GetHardwareInfoEventMessage(minionServer.getId(), minionServer.getMinionId()));

                    GetNetworkInfoEventMessageAction networkAction = new GetNetworkInfoEventMessageAction(SALT_SERVICE);
                    networkAction.execute(new GetNetworkInfoEventMessage(minionServer.getId()));

                    if (!hardwareAction.getErrors().isEmpty() || networkAction.getError() != null) {
                        sa.setStatus(ActionFactory.STATUS_FAILED);
                        sa.setResultMsg(
                            "Hardware list could not be refreshed completely\n" +
                                hardwareAction.getErrors().stream().collect(Collectors.joining("\n")) +
                                "\nNetwork: " + networkAction.getError()
                        );
                        sa.setResultCode(-1L);
                    } else {
                        sa.setStatus(ActionFactory.STATUS_COMPLETED);
                        sa.setResultMsg("hardware list refreshed");
                        sa.setResultCode(0L);

                    }
                    sa.setCompletionTime(new Date());

                    ActionFactory.save(sa);
                });

            });
        }
        else {
            LOG.error("Action not found: " + event.getActionId());
        }
    }
}
