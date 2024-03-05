/*
 * Copyright (c) 2009--2017 Red Hat, Inc.
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
package com.redhat.rhn.manager.kickstart;

import com.redhat.rhn.common.conf.Config;
import com.redhat.rhn.common.conf.ConfigDefaults;
import com.redhat.rhn.domain.channel.Channel;
import com.redhat.rhn.domain.kickstart.KickstartCommand;
import com.redhat.rhn.domain.kickstart.KickstartData;
import com.redhat.rhn.domain.kickstart.KickstartInstallType;
import com.redhat.rhn.domain.kickstart.KickstartPackage;
import com.redhat.rhn.domain.kickstart.KickstartScript;
import com.redhat.rhn.domain.kickstart.KickstartSession;
import com.redhat.rhn.domain.kickstart.KickstartVirtualizationType;
import com.redhat.rhn.domain.kickstart.RegistrationType;
import com.redhat.rhn.domain.kickstart.RepoInfo;
import com.redhat.rhn.domain.kickstart.cobbler.CobblerSnippet;
import com.redhat.rhn.domain.kickstart.crypto.CryptoKey;
import com.redhat.rhn.domain.token.ActivationKey;
import com.redhat.rhn.domain.token.ActivationKeyFactory;
import com.redhat.rhn.domain.token.Token;
import com.redhat.rhn.domain.user.User;
import com.redhat.rhn.domain.user.UserFactory;

import org.apache.commons.lang3.StringUtils;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashSet;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.List;

/**
 * Simple class to reduce dependencies between Struts and database layers
 *
 */
public class KickstartFormatter {

    private static Logger log = LogManager.getLogger(KickstartFormatter.class);


    private static final String REDHAT_REGISTER_SNIPPET = "spacewalk/redhat_register";
    private static final String REDHAT_REGISTER_USING_SALT_SNIPPET = "spacewalk/redhat_register_using_salt";
    private static final String POST_REACTIVATION_SNIPPET = "spacewalk/post_reactivation_key";
    private static final String POST_DELETION_SNIPPET = "spacewalk/post_delete_system";
    private static final String KEEP_SYSTEM_ID_SNIPPET = "spacewalk/keep_system_id";
    private static final String DEFAULT_MOTD = "spacewalk/default_motd";

    private static final String RAW_START = "#raw";
    private static final String RAW_END = "#end raw";
    private static final String NEWLINE = "\n";
    private static final String SPACE = " ";
    private static final String NO_BASE = "--nobase";
    private static final String IGNORE_MISSING = "--ignoremissing";
    private static final String PACKAGES = "%packages";
    private static final String END = "%end";
    private static final String INTERPRETER_OPT = "--interpreter";
    private static final String NOCHROOT = "--nochroot";
    private static final String ERRORONFAIL = "--erroronfail";
    private static final String HEADER = "# Kickstart config file generated by " +
        Config.get().getString("web.product_name") + " Config Management" +
        NEWLINE;
    private static final String COMMENT = "#" + NEWLINE;
    private static final String RHN_LOG_FILE = "/root/ks-rhn-post.log";
    private static final String BEGINRHN_LOG_APPEND = "# --Begin " +
            Config.get().getString("web.product_name") + " command section--" + NEWLINE;
    private static final String SAVE_KS_CFG = "cp `awk '{ if ($1 ~ /%include/) " +
        "{print $2}}' /tmp/ks.cfg` /tmp/ks.cfg /mnt/sysimage/root";

    private static final String  POST_LOG_FILE = "/root/ks-post.log";
    private static final String  POST_LOG_NOCHROOT_FILE = "/mnt/sysimage/root/ks-post.log";
    private static final String  PRE_LOG_FILE = "/tmp/ks-pre.log";

    private static final String KSTREE =
        "# now copy from the ks-tree we saved in the non-chroot checkout" + NEWLINE +
        "cp -fav /tmp/ks-tree-copy/* / 2>/dev/null" + NEWLINE +
        "rm -Rf /tmp/ks-tree-copy" + NEWLINE +
        "# --End " + Config.get().getString("web.product_name") + " command section--" +
        NEWLINE;
    public static final String[] UPDATE_PKG_NAMES =
    {"pyOpenSSL", "rhnlib", "libxml2-python", "libxml2"};
    public static final String[] FRESH_PKG_NAMES_RHEL8 =
    {"rhn-client-tools", "rhnsd", "dnf-plugin-spacewalk", "rhnlib", "spacewalk-koan"};
    public static final String[] FRESH_PKG_NAMES_RHEL8_FOR_SALT = {"salt-minion"};
    private static final String REMOTE_CMD =
        "mkdir -p /etc/sysconfig/rhn/allowed-actions/script" + NEWLINE +
        "touch /etc/sysconfig/rhn/allowed-actions/script/run";
    private static final String CONFIG_CMD =
        "mkdir -p /etc/sysconfig/rhn/allowed-actions/configfiles" + NEWLINE +
        "touch /etc/sysconfig/rhn/allowed-actions/configfiles/all";
    private static final String RHNCHECK = "rhn_check";
    private static final String RHN_NOCHROOT =
        "mkdir /mnt/sysimage/tmp/ks-tree-copy" + NEWLINE +
        "if [ -d /oldtmp/ks-tree-shadow ]; then" + NEWLINE +
        "cp -fa /oldtmp/ks-tree-shadow/* /mnt/sysimage/tmp/ks-tree-copy" + NEWLINE +
        "elif [ -d /tmp/ks-tree-shadow ]; then" + NEWLINE +
        "cp -fa /tmp/ks-tree-shadow/* /mnt/sysimage/tmp/ks-tree-copy" + NEWLINE +
        "fi" + NEWLINE +
        "cp /etc/resolv.conf /mnt/sysimage/etc/resolv.conf" + NEWLINE +
        "cp -f /tmp/ks-pre.log* /mnt/sysimage/root/ || :" + NEWLINE;
    private static final String RHN_TRACE = "set -x" + NEWLINE;
    private static final String XMLRPC_HOST =
        Config.get().getString(ConfigDefaults.KICKSTART_HOST, "xmlrpc.rhn.redhat.com");

    private static final String VIRT_HOST_GRUB_FIX =
        "sed -i.backup 's/default=[0-9]*/default=0/' /boot/grub/grub.conf" + NEWLINE;

    private static final String ISCRYPTED = "--iscrypted ";

    private static final String REDHAT_MGMT_SERVER = "$redhat_management_server";
    public static final String STATIC_NETWORK_VAR = "static_network";
    public static final String USE_IPV6_GATEWAY = "use_ipv6_gateway";
    public static final String KS_DISTRO = "ks_distro";
    private static final String STATIC_NETWORK_COMMAND = "network --bootproto static" +
                                                 " " + "--device %s" +
                                                 " " + "--gateway %s" +
                                                 " " + "--nameserver %s" +
                                                 " " + "--hostname %s";
    private static final String STATIC_NETWORK_COMMAND1 = " " + "--ip %s" +
                                                 " " + "--netmask %s";
    private static final String STATIC_NETWORK_COMMAND2 = " " + "--ipv6 %s";
    private static final String STATIC_NETWORK_COMMAND3 = " " + "--ipv6 %s/%s";

    private static final String NETWORK_STRING =
                                    "#if $varExists('%s')" + NEWLINE +
                                        "$%s" + NEWLINE +
                                   "#else" + NEWLINE +
                                        "%s" + NEWLINE +
                                   "#end if" + NEWLINE;

    private final KickstartData ksdata;
    private final String ksHost;
    private final User user;
    private KickstartSession session;
    private int postLogPostfix;
    private int preLogPostfix;

    /**
     * constructor
     * @param hostIn kickstart host
     * @param ksdataIn KickstartData
     */
    public KickstartFormatter(String hostIn, KickstartData ksdataIn) {

        this.ksdata = ksdataIn;
        this.ksHost = hostIn;
        this.user = UserFactory.findRandomOrgAdmin(this.ksdata.getOrg());
        this.postLogPostfix = 1;
        this.preLogPostfix = 1;
    }

    /**
     * Constructor with KickstartSession.
     * @param hostIn that is kickstarting from
     * @param ksdataIn that is is to be 'formatted' for output
     * @param sessionIn associated with the formatting.
     */
    public KickstartFormatter(String hostIn, KickstartData ksdataIn,
            KickstartSession sessionIn) {
        this(hostIn, ksdataIn);
        this.session = sessionIn;
    }

    private void addLogBegin(StringBuilder buff, String logFile, String interpreter) {
        if (ksdata.isRhel6OrGreater()) {
            buff.append(" --log " + logFile);
        }
        else if (isBashInterpreter(interpreter)) {
            buff.append(NEWLINE + "(");
        }
        buff.append(NEWLINE);
    }

    private void addLogEnd(StringBuilder buff, String logFile, String interpreter) {
        if (!ksdata.isRhel6OrGreater() && isBashInterpreter(interpreter)) {
            buff.append(") >> " + logFile + " 2>&1" + NEWLINE);
        }
    }

    /**
     *
     * @return String containing kickstart file
     */
    public String getFileData() {
        RegistrationType regType = ksdata.getRegistrationType(user);
        List<KickstartScript> l = new LinkedList<>(this.ksdata.getScripts());
        Collections.sort(l);
        List<KickstartScript> preScripts = new ArrayList<>();
        List<KickstartScript> postBeforeRedHatScripts = new ArrayList<>();
        List<KickstartScript> postAfterRedHatScripts = new ArrayList<>();
        for (KickstartScript ks : l) {
            if (ks.getScriptType().equals(KickstartScript.TYPE_PRE)) {
                preScripts.add(ks);
            }
            else if (ks.getPosition() < 0L) {
                postBeforeRedHatScripts.add(ks);
            }
            else {
                postAfterRedHatScripts.add(ks);
            }
        }
        StringBuilder buf = new StringBuilder();
        buf.append(getHeader());
        buf.append(getCommands());

        buf.append(NEWLINE);
        buf.append(getPackageOptions());
        buf.append(getPackages());
        buf.append(END + NEWLINE);
        buf.append(NEWLINE);
        buf.append("%" + KickstartScript.TYPE_PRE);
        buf.append(NEWLINE);

        addCobblerSnippet(buf, "autoinstall_start");
        buf.append(NEWLINE);
        addCobblerSnippet(buf, "pre_install_network_config");
        buf.append(NEWLINE);


        if (!RegistrationType.NONE.equals(regType)) {
            addCobblerSnippet(buf, KEEP_SYSTEM_ID_SNIPPET);
        }
        buf.append(END + NEWLINE);

        buf.append(renderScripts(preScripts));
        buf.append(NEWLINE);

        // This script should always be the first post script to run
        buf.append("%" + KickstartScript.TYPE_POST + SPACE + NOCHROOT + NEWLINE);
        buf.append(RHN_NOCHROOT + NEWLINE);
        if (this.ksdata.getKsCfg()) {
            buf.append(SAVE_KS_CFG + NEWLINE);
        }
        buf.append(END + NEWLINE);

        buf.append(renderScripts(postBeforeRedHatScripts));
        buf.append(NEWLINE);

        if (RegistrationType.REACTIVATION.equals(regType)) {
            addCobblerSnippet(buf, POST_REACTIVATION_SNIPPET);
            buf.append(END + NEWLINE);
        }
        else if (RegistrationType.DELETION.equals(regType)) {
            addCobblerSnippet(buf, POST_DELETION_SNIPPET);
            buf.append(END + NEWLINE);
        }

        buf.append(NEWLINE);
        buf.append(getRhnPost());
        buf.append(NEWLINE);
        buf.append(renderScripts(postAfterRedHatScripts));
        buf.append(NEWLINE);
        buf.append("%" + KickstartScript.TYPE_POST);    //new %post for last kernel stuff
        addCobblerSnippet(buf, "post_install_kernel_options");
        addCobblerSnippet(buf, "koan_environment");
        buf.append(NEWLINE);

        addCobblerSnippet(buf, "autoinstall_done");

        buf.append(NEWLINE);
        buf.append(END + NEWLINE);
        String retval = buf.toString();
        log.debug("fileData.retval:");
        log.debug(retval);
        return retval;
    }

    private void addCobblerSnippet(StringBuilder buf, String contents) {
        buf.append(CobblerSnippet.makeFragment(contents));
        buf.append(NEWLINE);
    }


    /**
     *
     * @return static string header
     */
    private StringBuffer getHeader() {
        StringBuffer header = new StringBuffer();
        header.append(ConfigDefaults.get().getKickstartTemplateHeader()).append(NEWLINE);
        header.append(HEADER);
        header.append(COMMENT);
        header.append("# Profile Label : " + this.ksdata.getLabel() + NEWLINE);
        header.append("# Date Created  : " + this.ksdata.getCreated() + NEWLINE);
        header.append(COMMENT);
        header.append(NEWLINE);

        return header;
    }

    /**
     *
     * @return string containing kickstart commands
     */
    private String getCommands() {
        StringBuilder commands = new StringBuilder();
        LinkedList<KickstartCommand> l = new LinkedList<>(this.ksdata.getCommands());
        Collections.sort(l);
        for (KickstartCommand command : l) {
            String cname = command.getCommandName().getName();
            log.debug("getCommands name: {}", cname);

            if (cname.matches("rootpw")) {
                commands.append(cname + SPACE + ISCRYPTED +
                        command.getArguments() + NEWLINE);
            }
            else if (cname.matches("url")) {
                if (command.getArguments() != null) {
                    String argVal = adjustUrlHost(command);

                    commands.append(cname + SPACE + argVal + NEWLINE);
                }
            }
            else if (cname.matches("repo")) {
                RepoInfo repo = RepoInfo.parse(command);
                commands.append(repo.getFormattedCommand(ksdata) + NEWLINE);
            }
            else if ("custom".equals(cname)) {
                commands.append(command.getArguments() + NEWLINE);
            }
            else if ("network".equals(cname)) {
                commands.append(String.format(NETWORK_STRING, STATIC_NETWORK_VAR,
                        STATIC_NETWORK_VAR,
                        cname + SPACE + command.getArguments()));
            }
            else {
                String argVal = command.getArguments();
                // some commands don't require an arg and are null in db
                if (argVal == null) {
                    commands.append(cname).append(NEWLINE);
                }
                else {
                    commands.append(cname + SPACE + argVal + NEWLINE);
                }
            }
        }

        if (!Config.get().getBoolean("ks_restrict_child_channels")) {
            for (Channel child : ksdata.getChildChannels()) {
                KickstartUrlHelper helper = new KickstartUrlHelper(ksdata);
                commands.append(String.format("repo --name=%s --baseurl=%s",
                      child.getLabel(), helper.getKickstartChildRepoUrl(child) + NEWLINE));
            }
        }
        commands.append(ksdata.getPartitionData() + NEWLINE);
        return commands.toString();
    }

    /**
     * Returns the network line for static networks
     * network --bootproto static --device $DEVICE --ip $IPADDR
     * --gateway $GATEWAY --nameserver $NAMESERVER
     *  --netmask $NETMASK --hostname $HOSTNAME
     * @param device the network interface name (eth0)
     * @param ip the ip address of the interface
     * @param gateway the gateway information of the card
     * @param nameServer the nameserver information
     * @param netmask the netmask information
     * @param hostName the host name information
     * @return the network* line for a static host
     */
    public static String makeStaticNetworkCommand(String device,
                            String ip, String gateway,
                            String nameServer, String netmask, String hostName) {
        return String.format(STATIC_NETWORK_COMMAND + STATIC_NETWORK_COMMAND1, device,
                                gateway, nameServer, hostName, ip, netmask);
    }

    /**
     * Returns the network line for static networks
     * network --bootproto static --device $DEVICE --ip $IPADDR --ipv6 $IP6ADDR
     * --gateway $GATEWAY --nameserver $NAMESERVER
     * --netmask $NETMASK --hostname $HOSTNAME
     * @param device the network interface name (eth0)
     * @param hostName the host name info
     * @param nameServer the nameserver info
     * @param ip4 the ipv4 address of the interface
     * @param nm4 the ipv4 netmask of the interface
     * @param gw4 the ipv4 gateway
     * @param ip6 the ipv6 address of the interface
     * @param nm6 the ipv6 netmask of the interface
     * @param gw6 the ipv6 gateway
     * @param preferIpv6Gateway whether or not should ipv6 gateway be prefered
     * @param ksDistro distro to be provisioned
     * @return the network* line for a static host
     */
    public static String makeStaticNetworkCommand(String device, String hostName,
            String nameServer, String ip4, String nm4, String gw4,
            String ip6, String nm6, String gw6, boolean preferIpv6Gateway,
            String ksDistro) {

        String gateway;
        if (preferIpv6Gateway && gw6 != null && !gw6.isEmpty()) {
            gateway = gw6;
        }
        else {
            gateway = gw4;
        }

        String command = String.format(STATIC_NETWORK_COMMAND, device, gateway,
            nameServer, hostName);

        if (ip4 != null && !ip4.isEmpty() && nm4 != null && !nm4.isEmpty()) {
            command += String.format(STATIC_NETWORK_COMMAND1, ip4, nm4);
        }
        else {
            command += " --noipv4";
        }

        if (ip6 != null && !ip6.isEmpty() && ksDistro != null &&
            (ksDistro.startsWith(KickstartInstallType.FEDORA_PREFIX) ||
             ksDistro.equals(KickstartInstallType.RHEL_6))) {
            if (nm6 == null || nm6.isEmpty() ||
                !ksDistro.startsWith(KickstartInstallType.FEDORA_PREFIX)) {
                command += String.format(STATIC_NETWORK_COMMAND2, ip6);
            }
            else {
                command += String.format(STATIC_NETWORK_COMMAND3, ip6, nm6);
            }
        }

        return command;
    }

    /**
     * Adjust the URL hostname if necessary. Hostnames are stored in the db as relative
     * paths if the user selects to use the default URL. When rendered we need to swap
     * in the most appropriate hostname.
     *
     * If this hostname appears to be customized, no change is made and we return the URL
     * as is.
     */
    private String adjustUrlHost(KickstartCommand command) {
        String argVal = command.getArguments();

        String urlLocation;
        if (argVal.startsWith("--url")) {
          urlLocation = argVal.substring("--url ".length());
        }
        else {
          urlLocation = argVal;
        }

        KickstartUrlHelper urlHelper = new KickstartUrlHelper(this.ksdata);

        log.debug("Got URL : {}", command.getArguments());
        log.debug("isRhnTree: {}", this.ksdata.getTree().isRhnTree());
        log.debug("Actual URL: {}", urlLocation);

        StringBuilder url = new StringBuilder();
        url.append("--url ");

        if (urlLocation.equals(this.ksdata.getTree().getAbsolutePath())) {
            log.debug("URL is not customized.");
            log.debug("Formatting for view use.");
            // /kickstart/dist/ks-rhel-i386-as-4-u2
            url.append(urlHelper.getCobblerMediaUrl());
            log.debug("constructed: {}", url);
            argVal = url.toString();
        }
        else if (urlLocation.startsWith("/")) {
            log.debug("URL is customized.");
            log.debug("Appending provided subpath to cobbler host.");
            url.append(urlHelper.getCobblerMediaUrlBase());
            url.append(urlLocation);
            log.debug("constructed: {}", url);
            argVal = url.toString();
        }
        else {
            log.debug("Just return the arg value.");
        }

        log.debug("returning url: {}", argVal);
        return argVal;
    }

    /**
     *
     * @return string containing package options
     */
    private String getPackageOptions() {
        String opts = "";

        if (this.ksdata.getIgnoreMissing()) {
            opts = opts + SPACE + IGNORE_MISSING;
        }
        if (this.ksdata.getNoBase() && !this.ksdata.isRhel8() && !this.ksdata.isFedora()) {
            opts = opts + SPACE + NO_BASE;
        }
        return PACKAGES + SPACE + opts + NEWLINE;
    }

    /**
     *
     * @return string containing packages
     */
    private String getPackages() {
        StringBuilder buf = new StringBuilder();
        for (KickstartPackage kp : ksdata.getKsPackages()) {
            buf.append(kp.getPackageName().getName() + NEWLINE);
        }
        if (KickstartVirtualizationType.paraHost().equals(ksdata.getKickstartDefaults().
                getVirtualizationType())) {
            buf.append("kernel-xen" + NEWLINE);
            buf.append("xen" + NEWLINE);
        }

        // packages necessary for rhel2.1
        if (ConfigDefaults.get().getUserSelectedSaltInstallTypeLabels().contains(ksdata.getInstallType().getLabel())) {
         // packages necessary for RHEL 6+ and Fedora (salt)
            buf.append("venv-salt-minion" + NEWLINE);
        }
        else if (this.ksdata.isRhel7OrGreater() || this.ksdata.isFedora()) {
            // packages necessary for RHEL 7 and Fedora (traditional)
            buf.append("perl" + NEWLINE);
            buf.append("wget" + NEWLINE);
            buf.append("rhn-setup" + NEWLINE);
            buf.append("rhn-check" + NEWLINE);
            buf.append("rhn-client-tools" + NEWLINE);
        }
        return buf.toString();
    }

    /**
     * @param scripts the kickstart scripts we want to render
     * @return rendered script(s)
     */
    private String renderScripts(List<KickstartScript> scripts) {
        StringBuilder retval = new StringBuilder();
        for (KickstartScript kss : scripts) {
            boolean isPre = kss.getScriptType().equals(KickstartScript.TYPE_PRE);

            retval.append(NEWLINE);
            if (kss.getRaw()) {
                retval.append(RAW_START + NEWLINE);
            }
            String command = "%" + kss.getScriptType();
            if (!isPre && !kss.thisScriptIsChroot()) {
                command += SPACE + NOCHROOT;
            }
            if (kss.getErrorOnFail()) {
                command += SPACE + ERRORONFAIL;
            }
            if (!StringUtils.isBlank(kss.getInterpreter())) {
                command += SPACE + INTERPRETER_OPT + SPACE + kss.getInterpreter();
            }
            retval.append(command);
            if (ksdata.getPreLog() && isPre) {
                addLogBegin(retval, PRE_LOG_FILE + "." + this.preLogPostfix,
                        kss.getInterpreter());
            }
            else if (ksdata.getPostLog() && !isPre && kss.thisScriptIsChroot()) {
                addLogBegin(retval, POST_LOG_FILE + "." + this.postLogPostfix,
                        kss.getInterpreter());
            }
            else if (ksdata.getNonChrootPost() && !isPre && !kss.thisScriptIsChroot()) {
                addLogBegin(retval, POST_LOG_NOCHROOT_FILE + "." + this.postLogPostfix,
                        kss.getInterpreter());
                if (isBashInterpreter(kss.getInterpreter())) {
                    retval.append(RHN_TRACE);
                }
            }
            else {
                retval.append(NEWLINE);
            }

            retval.append(kss.getDataContents() + NEWLINE);

            if (ksdata.getPreLog() && isPre) {
                addLogEnd(retval, PRE_LOG_FILE + "." + kss.getPosition(),
                        kss.getInterpreter());
                this.preLogPostfix += 1;
            }
            else if (ksdata.getPostLog() && !isPre && kss.thisScriptIsChroot()) {
                addLogEnd(retval, POST_LOG_FILE + "." + this.postLogPostfix,
                        kss.getInterpreter());
                this.postLogPostfix += 1;
            }
            else if (ksdata.getNonChrootPost() && !isPre && !kss.thisScriptIsChroot()) {
                addLogEnd(retval, POST_LOG_NOCHROOT_FILE + "." + this.postLogPostfix,
                        kss.getInterpreter());
                this.postLogPostfix += 1;
            }

            if (kss.getRaw()) {
                retval.append(RAW_END + NEWLINE);
            }
            retval.append(END + NEWLINE);
        } // end loop
        return retval.toString();
    }

    private String getRhnPost() {
        log.debug("getRhnPost called.");
        StringBuilder retval = new StringBuilder();
        retval.append("%" + KickstartScript.TYPE_POST);
        addLogBegin(retval, RHN_LOG_FILE, "");
        retval.append(BEGINRHN_LOG_APPEND);

        retval.append(renderKeys() + NEWLINE);

        if (this.ksdata.getKickstartDefaults().getVirtualizationType()
                .getLabel().equals("para_host")) {
            retval.append(VIRT_HOST_GRUB_FIX);
        }

        if (log.isDebugEnabled()) {
            log.debug("kickstart_host: [{}] kshost: [{}] indexof: {}", XMLRPC_HOST, this.ksHost,
                    this.ksHost.indexOf(XMLRPC_HOST));
        }

        String up2datehost = REDHAT_MGMT_SERVER;
        //check if server going through Spacewalk Proxy,
        //if so, register through proxy instead
        if (this.session != null &&
                this.session.getSystemRhnHost() != null &&
                !this.session.getSystemRhnHost().equals("unknown")) {
            up2datehost = this.session.getSystemRhnHost();
        }

        if (!ConfigDefaults.get().getUserSelectedSaltInstallTypeLabels().contains(ksdata.getInstallType().getLabel())) {
            log.debug("adding perl -npe for /etc/sysconfig/rhn/up2date");
            // both rhel 2 and rhel3/4 need the following
            retval.append("perl -npe " +
                    "'s|^(\\s*(noSSLS\\|s)erverURL\\s*=\\s*[^:]+://)[^/]*/|\\${1}" +
                    up2datehost +
                    "/|' -i /etc/sysconfig/rhn/up2date" + NEWLINE);

            if (this.ksdata.getVerboseUp2date()) {
                retval.append("[ -r /etc/sysconfig/rhn/up2date ] && " +
                        "sed 's/debug=0/debug=1/' -i /etc/sysconfig/rhn/up2date" +
                        NEWLINE);
            }
        }

        if (this.ksdata.getVerboseUp2date()) {
            retval.append("[ -r /etc/yum.conf ] && " +
                    "sed 's/debuglevel=2/debuglevel=5/' -i /etc/yum.conf" +
                    NEWLINE);
        }

        if (this.ksdata.getKickstartDefaults().getRemoteCommandFlag()) {
            retval.append(REMOTE_CMD + NEWLINE);
        }

        if (this.ksdata.getKickstartDefaults().getCfgManagementFlag()) {
            retval.append(CONFIG_CMD + NEWLINE);
        }

        retval.append(NEWLINE);
        retval.append(KSTREE);
        retval.append(NEWLINE);

        retval.append("# begin cobbler snippet" + NEWLINE);
        retval.append(NEWLINE);
        // Work around for bug #522251
        if (!this.ksdata.getKickstartDefaults().getKstree().getChannel().
             getChannelArch().getName().startsWith("s390")) {
            addCobblerSnippet(retval, "post_install_network_config");
        }

        addCobblerSnippet(retval, DEFAULT_MOTD);

        if (ConfigDefaults.get().getUserSelectedSaltInstallTypeLabels().contains(ksdata.getInstallType().getLabel())) {
            addCobblerSnippet(retval, REDHAT_REGISTER_USING_SALT_SNIPPET);
        }
        else {
            addCobblerSnippet(retval, REDHAT_REGISTER_SNIPPET);
            retval.append(NEWLINE);
            retval.append(RHNCHECK + NEWLINE);
        }

        retval.append("# end cobbler snippet" + NEWLINE);

        addLogEnd(retval, RHN_LOG_FILE, "");

        retval.append(END + NEWLINE);
        return retval.toString();
    }

    /**
     * Generate a comma separated list of activation keys to use with the
     * associated KickstartData and KickstartSession
     * @param ksdata to get list from
     * @param ksession session containing keys
     *
     * @return String list of activationkeys separated by comman
     */
    public static String generateActivationKeyString(KickstartData ksdata,
            KickstartSession ksession) {
        StringBuilder retval = new StringBuilder();
        List<ActivationKey> tokens = generateActKeyTokens(ksdata, ksession);
        for (Iterator<ActivationKey> itr = tokens.iterator(); itr.hasNext();) {
            ActivationKey act = itr.next();
            log.debug("rhnreg: key name: {}", act.getKey());
            retval.append(act.getKey());
            if (itr.hasNext()) {
                retval.append(",");
            }
        }
        log.debug("generateActivationKeyString: {}", retval);
        return retval.toString();
    }

    private static List<ActivationKey> generateActKeyTokens(KickstartData ksdata,
            KickstartSession ksession) {
        List<ActivationKey> tokens = new ArrayList<>();
        log.debug("Computing Activation Keys");
        // If we are in a KickstartSession and dont have any activation keys
        // associated with this KickstartProfile then we want to create a
        // one time key.
        if (log.isDebugEnabled()) {
            log.debug("def reg tokens: {}", ksdata.getDefaultRegTokens());
        }

        ActivationKey defaultKey = ksession == null ? null :
            ActivationKeyFactory.lookupByKickstartSession(ksession);

        log.debug("generateActKeyTokens :: defaultKey: {}", defaultKey);

        //if we need a reactivation key, add one
        if (defaultKey != null) {
            log.debug("Session isn't null.  Lets use the profile's activation key.");
                tokens.add(defaultKey);
                if (log.isDebugEnabled()) {
                    log.debug("Found one time activation key: {}", defaultKey.getKey());
                }
        }
        log.debug("tokens size: {}", tokens.size());
        //add the activation keys associated with the kickstart profile
        if (ksdata.getDefaultRegTokens() != null && !ksdata.getDefaultRegTokens().isEmpty()) {
            for (Token tk : ksdata.getDefaultRegTokens()) {
                ActivationKey act =
                        ActivationKeyFactory.lookupByToken(tk);
                tokens.add(act);
            }
        }
        return tokens;
    }

    private String renderKeys() {
        StringBuilder retval = new StringBuilder();

        HashSet<CryptoKey> sslKeys = new HashSet<>();
        HashSet<CryptoKey> gpgKeys = new HashSet<>();

        // setup keys for rendering
        if (this.ksdata.getCryptoKeys() != null) {
            for (CryptoKey tmpKey : this.ksdata.getCryptoKeys()) {
                if (tmpKey.isGPG()) {
                    gpgKeys.add(tmpKey);
                }
                else if (tmpKey.isSSL()) {
                    sslKeys.add(tmpKey);
                }
            }
        }

        if (!gpgKeys.isEmpty()) {
            retval.append(renderGpgKeys(gpgKeys));
        }

        if (!ConfigDefaults.get().getUserSelectedSaltInstallTypeLabels()
                .contains(ksdata.getInstallType().getLabel()) && !sslKeys.isEmpty()) {
            retval.append(renderSslKeys(sslKeys));
        }
        return retval.toString();
    }

    /**
     * Helper method to render gpg keys for kickstart file
     * @param setIn of gpg keys for this kickstart
     * @return rendered gpg key string for kickstart
     */
    private String renderGpgKeys(HashSet<CryptoKey> setIn) {
        StringBuilder retval = new StringBuilder();
        int peg = 1;
        for (CryptoKey myKey : setIn) {
            retval.append("cat > /tmp/gpg-key-" + peg + " <<'EOF'" + NEWLINE);
            retval.append(myKey.getKeyString() + NEWLINE);
            retval.append("EOF\n# gpg-key" + peg + NEWLINE);
            retval.append("rpm --import /tmp/gpg-key-" + peg + NEWLINE);
            peg++;
        }
        return retval.toString();
    }

    /**
     * Helper method to render ssl keys for kickstart file
     * @param setIn of sll keys for this kickstart
     * @return rendered sll key string for kickstart
     */
    private String renderSslKeys(HashSet<CryptoKey> setIn) {
        StringBuilder retval = new StringBuilder();
        int peg = 1;
        for (CryptoKey myKey : setIn) {
            retval.append("cat > /tmp/ssl-key-" + peg + " <<'EOF'" + NEWLINE);
            retval.append(myKey.getKeyString() + NEWLINE);
            retval.append(NEWLINE);
            retval.append("EOF\n# ssl-key" + peg + NEWLINE);
            peg++;
        }

        retval.append("cat /tmp/ssl-key-* > /usr/share/rhn/RHN-ORG-TRUSTED-SSL-CERT" + NEWLINE);
        retval.append("sed 's/RHNS-CA-CERT/RHN-ORG-TRUSTED-SSL-CERT/g' -i /etc/sysconfig/rhn/up2date" + NEWLINE);

        return retval.toString();
    }

    /**
     * Detects whether the interpreter is set to bash
     * @param interpreter interpreter
     * @return True if interpreter is bash
     */
    private boolean isBashInterpreter(String interpreter) {
        return StringUtils.isBlank(interpreter) || interpreter.endsWith("bash");
    }
}
