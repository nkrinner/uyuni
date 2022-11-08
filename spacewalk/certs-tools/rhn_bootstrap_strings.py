#
# Copyright (c) 2008--2018 Red Hat, Inc.
# Copyright (c) 2016--2021 SUSE LLC.
#
# This software is licensed to you under the GNU General Public License,
# version 2 (GPLv2). There is NO WARRANTY for this software, express or
# implied, including the implied warranties of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. You should have received a copy of GPLv2
# along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.
#
# Red Hat trademarks are not licensed under GPLv2. No permission is
# granted to use or replicate Red Hat trademarks that are incorporated
# in this software or its documentation.
#
#
# shell script function library for rhn-bootstrap
#
from uyuni.common.context_managers import cfg_component
from spacewalk.common.rhnConfig import isUyuni
import os.path


_header = """\
#!/bin/bash

# In case the script is executed using different interpreter than bash
# then we call the script explicitely using bash
SHPATH=$(readlink /proc/$$/exe)
if ! [ "$SHPATH" = "/bin/bash" -o "$SHPATH" = "/usr/bin/bash" ]; then
  exec bash "$0" "$@"
fi

echo "{productName} Client bootstrap script v{version}"

# This file was autogenerated. Minor manual editing of this script may be
# necessary to complete the bootstrap setup. Once customized, the bootstrap
# script can be triggered in one of two ways (the first is preferred):
#
#   (1) centrally, from the {productName} via ssh (i.e., from the
#       {productName}):
#         cd {apachePubDirectory}/bootstrap/
#         cat bootstrap-<edited_name>.sh | ssh root@<client-hostname> /bin/bash
#
#   ...or...
#
#   (2) in a decentralized manner, executed on each client, via wget or curl:
#         wget -qO- https://{hostname}/pub/bootstrap/bootstrap-<edited_name>.sh | /bin/bash
#         ...or...
#         curl -Sks https://{hostname}/pub/bootstrap/bootstrap-<edited_name>.sh | /bin/bash

# SECURITY NOTE:
#   Use of these scripts via the two methods discussed is the most expedient
#   way to register machines to your {productName}. Since "wget" is used
#   throughout the script to download various files, a "Man-in-the-middle"
#   attack is theoretically possible.
#
#   The actual registration process is performed securely via SSL, so the risk
#   is minimized in a sense. This message merely serves as a warning.
#   Administrators need to appropriately weigh their concern against the
#   relative security of their internal network.

# PROVISIONING/KICKSTART NOTE:
#   If provisioning a client, ensure the proper CA SSL public certificate is
#   configured properly in the post section of your kickstart profiles (the
#   {productName} or hosted web user interface).

# REGISTER VERSIONING NOTE:
#   This script will not work with traditional spacewalk registration tools.


echo
echo
echo "MINOR MANUAL EDITING OF THIS FILE MAY BE REQUIRED!"
echo
echo "If this bootstrap script was created during the initial installation"
echo "of a {productName}, the ACTIVATION_KEYS, and ORG_GPG_KEY values will"
echo "probably *not* be set (see below). If this is the case, please do the"
echo "following:"
echo "  - copy this file to a name specific to its use."
echo "    (e.g., to bootstrap-SOME_NAME.sh - like bootstrap-web-servers.sh.)"
echo "  - on the website create an activation key or keys for the system(s) to"
echo "    be registered."
echo "  - edit the values of the VARIABLES below (in this script) as"
echo "    appropriate:"
echo "    - ACTIVATION_KEYS needs to reflect the activation key(s) value(s)"
echo "      from the website. XKEY or XKEY,YKEY"
echo "      Please note that if you are using this script to boostrap minions,"
echo "      only the FIRST activation key will be used. Multiple activation keys"
echo "      are not supported with salt"
echo "    - ORG_GPG_KEY needs to be set to the name(s) of the corporate public"
echo "      GPG key filename(s) (residing in {apachePubDirectory}) if appropriate. XKEY or XKEY,YKEY"
echo "    - When reactivating Salt minion, use REACTIVATION_KEY variable"
echo "      Consider using environmental variable REACTIVATION_KEY for single use reactivation keys."
echo

# can be edited, but probably correct (unless created during initial install):
# NOTE: ACTIVATION_KEYS *must* be used to bootstrap a client machine.
ACTIVATION_KEYS={activation_keys}
ORG_GPG_KEY={org_gpg_key}

# To reactivate single Salt client use following variable:
# NOTE: Reactivation keys are removed valid only for single use.
#       It is also possible to use REACTIVATION_KEY environmental variable.
REACTIVATION_KEY=${{REACTIVATION_KEY:-}}

# can be edited, but probably correct:
CLIENT_OVERRIDES={overrides}
HOSTNAME={hostname}

ORG_CA_CERT={orgCACert}

USING_SSL={using_ssl}
USING_GPG={using_gpg}

REGISTER_THIS_BOX=1

# Set if you want to specify profilename for client systems.
# NOTE: Make sure it's set correctly if any external command is used.
#
# ex. PROFILENAME="foo.example.com"  # For specific client system
#     PROFILENAME=`hostname -s`      # Short hostname
#     PROFILENAME=`hostname -f`      # FQDN
PROFILENAME=""   # Empty by default to let it be set automatically.

# SUSE Manager Specific settings:
#
# - Alternate location of the client tool repos providing 
#   packages required for registration. Unless they are already installed on the
#   client this repo is expected to provide them:
#   ${{CLIENT_REPOS_ROOT}}/sle/VERSION/PATCHLEVEL
# If empty, the SUSE Manager repositories provided at https://${{HOSTNAME}}/pub/repositories
# are used.
CLIENT_REPOS_ROOT=
{venv_section}

# Automatically schedule reboot of the machine in case of running transactional
# system (for example SLE Micro)
SCHEDULE_REBOOT_AFTER_TRANSACTION=1

#
# -----------------------------------------------------------------------------
# DO NOT EDIT BEYOND THIS POINT -----------------------------------------------
# -----------------------------------------------------------------------------
#

VENV_ENABLED=0

#
# do not try to register a SUSE Manager server at itself
#
MYNAME=`hostname -f`
LCMYNAME=`echo $MYNAME | tr '[:upper:]' '[:lower:]'`
LCHOSTNAME=`echo $HOSTNAME | tr '[:upper:]' '[:lower:]'`

if [ "$LCMYNAME" == "$LCHOSTNAME" ]; then
    echo "Name of client and of SUSE Manager server are the same."
    echo "Do not try to register a SUSE Manager server at itself!"
    echo "Aborting."
    exit 1
fi

# an idea from Erich Morisse (of Red Hat).
# use either wget *or* curl
# Also check to see if the version on the
# machine supports the insecure mode and format
# command accordingly.

if [ -x /usr/bin/wget ]; then
    output=`LANG=en_US /usr/bin/wget --no-check-certificate 2>&1`
    error=`echo $output | grep "unrecognized option"`
    if [ -z "$error" ]; then
        FETCH="/usr/bin/wget -nv -r -nd --no-check-certificate"
    else
        FETCH="/usr/bin/wget -nv -r -nd"
    fi
elif [ -x /usr/bin/curl ]; then
    output=`LANG=en_US /usr/bin/curl -k 2>&1`
    error=`echo $output | grep "is unknown"`
    if [ -z "$error" ]; then
        FETCH="/usr/bin/curl -ksSOf"
    else
        FETCH="/usr/bin/curl -sSOf"
    fi
else
    echo "To be able to download files, please install either 'wget' or 'curl'"
    exit 1
fi

HTTP_PUB_DIRECTORY=http://${{HOSTNAME}}/{pubname}
HTTPS_PUB_DIRECTORY=https://${{HOSTNAME}}/{pubname}
if [ $USING_SSL -eq 0 ]; then
    HTTPS_PUB_DIRECTORY=${{HTTP_PUB_DIRECTORY}}
fi

INSTALLER=zypper

if [ -x /usr/bin/dnf ]; then
    INSTALLER=yum
elif [ -x /usr/bin/zypper ]; then
    INSTALLER=zypper
elif [ -x /usr/bin/yum ]; then
    INSTALLER=yum
elif [ -x /usr/bin/apt ]; then
    INSTALLER=apt
fi


SNAPSHOT_ID=""

function call_tukit() {{
    tukit -q call $SNAPSHOT_ID /bin/bash <<< $@
}}

function new_transaction() {{
    if [ -n "$SNAPSHOT_ID" ]; then
        tukit -q close $SNAPSHOT_ID
    fi
    SNAPSHOT_ID=$(/usr/sbin/tukit -q open | sed 's/ID: \([0-9]*\)/\\1/')
    if [ -z "$SNAPSHOT_ID" ]; then
        echo "Transactional system detected, but could not open new transaction. Aborting!"
        exit 1
    fi
}}

if [ -x /usr/sbin/tukit ]; then
    new_transaction
    echo "Transactional system detected. Reboot will be required to finish bootstrapping"
    cat > /etc/tukit.conf <<EOL
# Access /root in the snapshot
BINDDIRS[0]="/root"
EOL
fi

if [ ! -w . ]; then
    echo ""
    echo "*** ERROR: $(pwd):"
    echo "    No permission to write to the current directory."
    echo "    Please execute this script in a directory where downloaded files can be stored."
    echo ""
    exit 1
fi
"""


def getHeader(productName, options, orgCACert, pubname, apachePubDirectory):
    # 11/22/16 options.gpg_key is now a comma-separated list of path.
    # Removing paths from options.gpg_key
    org_gpg_key = ",".join([os.path.basename(gpg_key) for gpg_key in options.gpg_key.split(",")])
    with cfg_component('web') as CFG:
        version = CFG.version
        if isUyuni():
            version = CFG.uyuni

    venv_section = """
# Avoid installing venv-salt-minion instead salt-minion
# even if it available in the bootstrap repo
AVOID_VENV_SALT_MINION={avoid_venv}

# Force installing venv-salt-minion instead salt-minion
# even if it is NOT available in the bootstrap repo
FORCE_VENV_SALT_MINION={force_venv}
""".format(
    avoid_venv=1 if bool(options.no_bundle) else 0,
    force_venv=1 if bool(options.force_bundle) else 0,
) or ""

    return _header.format(productName=productName,
                          version=version,
                          apachePubDirectory=apachePubDirectory,
                          activation_keys=options.activation_keys,
                          org_gpg_key=org_gpg_key,
                          overrides=options.overrides,
                          hostname=options.hostname,
                          orgCACert=orgCACert,
                          venv_section=venv_section,
                          using_ssl=1,
                          using_gpg=0 if bool(options.no_gpg) else 1,
                          pubname=pubname)

def getRegistrationStackSh():
    """
    Determines which packages and repositories needs to be
    installed in order to register this system against SUMa server.
    """
    PKG_NAME = ['salt', 'salt-minion']
    PKG_NAME_YUM = ['salt', 'salt-minion']
    PKG_NAME_VENV = ['venv-salt-minion']

    PKG_NAME_UPDATE = list(PKG_NAME)
    PKG_NAME_UPDATE.extend(['zypper', 'openssl'])

    PKG_NAME_VENV_UPDATE = list(PKG_NAME_VENV)
    PKG_NAME_VENV_UPDATE.extend(['zypper', 'openssl'])

    PKG_NAME_UPDATE_YUM = list(PKG_NAME_YUM)
    PKG_NAME_UPDATE_YUM.extend(['yum', 'openssl'])

    PKG_NAME_VENV_UPDATE_YUM = list(PKG_NAME_VENV)
    PKG_NAME_VENV_UPDATE_YUM.extend(['yum', 'openssl'])

    TEST_VENV_FUNC = """
function test_venv_enabled() {
    if [ $FORCE_VENV_SALT_MINION -eq 1 ]; then
        VENV_ENABLED=1
    elif [ $AVOID_VENV_SALT_MINION -ne 1 ]; then
        local repourl="$CLIENT_REPO_URL"
        if [ "$INSTALLER" == "zypper" ] || [ "$INSTALLER" == "yum" ]; then
            ARCH=$(rpm --eval "%{_arch}")
        else
            ARCH=$(dpkg --print-architecture)
        fi
        VENV_FILE="venv-enabled-$ARCH.txt"
        $FETCH $repourl/$VENV_FILE
        if [ -f "$VENV_FILE" ]; then
            echo "Bootstrap repo '$repourl' contains salt bundle."
            repourl=""
            VENV_ENABLED=1
        fi
        rm -f "$VENV_FILE"
    fi
}
"""
    TEST_VENV_CALL = """
    test_venv_enabled
"""

    return """\
echo
echo "CLEANING UP OLD SUSE MANAGER REPOSITORIES"
echo "-------------------------------------------------"

function clean_up_old_trad_repos() {{
    local trad_client_repo_prefix="spacewalk:"
    if [ -f /usr/bin/realpath ]; then
        GET_PATH="/usr/bin/realpath"
    else
        GET_PATH="/usr/bin/readlink -f --"
    fi

    for file in $1/$trad_client_repo_prefix*.repo; do
        if [ -f "$file" ]; then
            echo "Removing $($GET_PATH "$file")"
            rm -f $($GET_PATH "$file")
        fi
    done
}}

function clean_up_old_salt_repos() {{
    if [ -f "$1" ]; then
        echo "Removing $1"
        rm -f "$1"
    fi
}}

function clean_up_old_repos() {{
    clean_up_old_salt_repos "/etc/zypp/repos.d/susemanager:channels.repo"
    clean_up_old_salt_repos "/etc/yum.repos.d/susemanager:channels.repo"
    clean_up_old_salt_repos "/etc/apt/sources.list.d/susemanager:channels.list"

    clean_up_old_trad_repos "/etc/zypp/repos.d"
    clean_up_old_trad_repos "/etc/yum.repos.d"
}}

clean_up_old_repos
echo
echo "CHECKING THE REGISTRATION STACK"
echo "-------------------------------------------------"

function test_repo_exists() {{
    local repourl="$CLIENT_REPO_URL"

    $FETCH $repourl/repodata/repomd.xml
    if [ ! -f "repomd.xml" ]; then
        echo "Bootstrap repo '$repourl' does not exist."
        repourl=""
        CLIENT_REPO_URL=""
    fi
    rm -f repomd.xml
}}
{TEST_VENV_FUNC}

function setup_bootstrap_repo() {{
    local repopath="$CLIENT_REPO_FILE"
    local reponame="$CLIENT_REPO_NAME"
    local repourl="$CLIENT_REPO_URL"

    test_repo_exists

    if [ -n "$CLIENT_REPO_URL" ]; then
        echo " adding client software repository at $repourl"
        cat <<EOF >"$repopath"
[$reponame]
name=$reponame
baseurl=$repourl
enabled=1
autorefresh=1
keeppackages=0
gpgcheck=0
EOF
    fi

    # Avoid modularity failsafe mechanism in dnf 4.2.7 or greater
    if [ -n "$Y_CLIENT_CODE_VERSION" ] && [ $Y_CLIENT_CODE_VERSION -ge 8 ]; then
        echo " adding 'module_hotfixes' flag to the repository config"
        echo "module_hotfixes=1" >> "$repopath"
    fi
}}

function remove_bootstrap_repo() {{
    local repopath="$CLIENT_REPO_FILE"

    rm -f $repopath
}}

if [ "$INSTALLER" == yum ]; then
    function getY_CLIENT_CODE_BASE() {{
        local BASE=""
        local VERSION=""
        # SLES ES6 is a special case; it will install a symlink named
        # centos-release pointing to redhat-release which will make the
        # original test fail; reverting the checks does not help as this
        # will break genuine CentOS systems. So use the poor man's approach
        # to detect this special case. SLES ES7 does not have this issue
        # https://bugzilla.suse.com/show_bug.cgi?id=1132576
        # https://bugzilla.suse.com/show_bug.cgi?id=1152795
        if [ -L /usr/share/doc/sles_es-release ]; then
            BASE="res"
            VERSION=6
        elif [ -f /etc/almalinux-release ]; then
            grep -v '^#' /etc/almalinux-release | grep -q '\(AlmaLinux\)' && BASE="almalinux"
            VERSION=`grep -v '^#' /etc/almalinux-release | grep -Po '(?<=release )\d+'`
        elif [ -f /etc/rocky-release ]; then
            grep -v '^#' /etc/rocky-release | grep -q '\(Rocky Linux\)' && BASE="rockylinux"
            VERSION=`grep -v '^#' /etc/rocky-release | grep -Po '(?<=release )\d+'`
        elif [ -f /etc/oracle-release ]; then
            grep -v '^#' /etc/oracle-release | grep -q '\(Oracle\)' && BASE="oracle"
            VERSION=`grep -v '^#' /etc/oracle-release | grep -Po '(?<=release )\d+'`
        elif [ -f /etc/alinux-release ]; then
            grep -v '^#' /etc/alinux-release | grep -q '\(Alibaba\)' && BASE="alibaba"
            VERSION=`grep -v '^#' /etc/alinux-release | grep -Po '(?<=release )\d+'`
        elif [ -f /etc/centos-release ]; then
            grep -v '^#' /etc/centos-release | grep -q '\(CentOS\)' && BASE="centos"
            VERSION=`grep -v '^#' /etc/centos-release | grep -Po '(?<=release )\d+'`
        elif [ -f /etc/redhat-release ]; then
            grep -v '^#' /etc/redhat-release | grep -q '\(Red Hat\)' && BASE="res"
            VERSION=`grep -v '^#' /etc/redhat-release | grep -Po '(?<=release )\d+'`
        elif [ -f /etc/os-release ]; then
            BASE=$(source /etc/os-release; echo $ID)
            VERSION=$(source /etc/os-release; echo $VERSION_ID)
        fi
        Y_CLIENT_CODE_BASE="${{BASE:-unknown}}"
        Y_CLIENT_CODE_VERSION="${{VERSION:-unknown}}"
    }}

    function getY_MISSING() {{
        local NEEDED="{PKG_NAME_YUM}"
        if [ $VENV_ENABLED -eq 1 ]; then
            NEEDED="{PKG_NAME_VENV}"
        fi
        Y_MISSING=""
        for P in $NEEDED; do
            rpm -q "$P" || Y_MISSING="$Y_MISSING $P"
        done
    }}

    echo "* check for necessary packages being installed..."
    getY_CLIENT_CODE_BASE
    echo "* client codebase is ${{Y_CLIENT_CODE_BASE}}-${{Y_CLIENT_CODE_VERSION}}"

    CLIENT_REPOS_ROOT="${{CLIENT_REPOS_ROOT:-https://${{HOSTNAME}}/pub/repositories}}"
    CLIENT_REPO_URL="${{CLIENT_REPOS_ROOT}}/${{Y_CLIENT_CODE_BASE}}/${{Y_CLIENT_CODE_VERSION}}/bootstrap"
    CLIENT_REPO_NAME="susemanager:bootstrap"
    CLIENT_REPO_FILE="/etc/yum.repos.d/$CLIENT_REPO_NAME.repo"

    # In case of Red Hat derivatives, check if bootstrap repository is available, if not, fallback to RES.
    if [ "$Y_CLIENT_CODE_BASE" == almalinux ] || \
      [ "$Y_CLIENT_CODE_BASE" == rockylinux ] || \
      [ "$Y_CLIENT_CODE_BASE" == oracle ] || \
      [ "$Y_CLIENT_CODE_BASE" == alibaba ] || \
      [ "$Y_CLIENT_CODE_BASE" == centos ] ; then
        $FETCH $CLIENT_REPO_URL/repodata/repomd.xml &> /dev/null
        if [ $? -ne 0 ]; then
            echo "${{Y_CLIENT_CODE_BASE}} ${{Y_CLIENT_CODE_VERSION}} bootstrap repository not found, using RES${{Y_CLIENT_CODE_VERSION}} bootstrap repository instead"
            CLIENT_REPO_URL="${{CLIENT_REPOS_ROOT}}/res/${{Y_CLIENT_CODE_VERSION}}/bootstrap"
        fi
    fi

    setup_bootstrap_repo
{TEST_VENV_CALL}
    getY_MISSING

    if [ -z "$Y_MISSING" ]; then
        echo "  no packages missing."
    else
        echo "* going to install missing packages..."

        yum -y install $Y_MISSING

        for P in $Y_MISSING; do
            rpm -q "$P" || {{
            echo "ERROR: Failed to install all missing packages."
            exit 1
        }}
        done
    fi
    # try update main packages for registration from any repo which is available
    if [ $VENV_ENABLED -eq 1 ]; then
        yum -y upgrade {PKG_NAME_VENV_UPDATE_YUM} ||:
    else
        yum -y upgrade {PKG_NAME_UPDATE_YUM} $RHNLIB_PKG ||:
    fi

elif [ "$INSTALLER" == zypper ]; then
    function getZ_CLIENT_CODE_BASE() {{
        local BASE=""
        local VERSION=""
        local PATCHLEVEL=""
        if [ -r /etc/SuSE-release ]; then
            grep -q 'Enterprise' /etc/SuSE-release && BASE='sle'
            eval $(grep '^\(VERSION\|PATCHLEVEL\)' /etc/SuSE-release | tr -d '[:blank:]')
            if [ "$BASE" != "sle" ]; then
                grep -q 'openSUSE' /etc/SuSE-release && BASE='opensuse'
                VERSION="$(grep '^\(VERSION\)' /etc/SuSE-release | tr -d '[:blank:]' | sed -n 's/.*=\([[:digit:]]\+\).*/\\1/p')"
                PATCHLEVEL="$(grep '^\(VERSION\)' /etc/SuSE-release | tr -d '[:blank:]' | sed -n 's/.*\.\([[:digit:]]*\).*/\\1/p')"
            fi
        elif [ -r /etc/os-release ]; then
            grep -q 'Enterprise' /etc/os-release && BASE='sle'
            if [ "$BASE" != "sle" ]; then
                grep -q 'openSUSE' /etc/os-release && BASE='opensuse'
            fi
            grep -q 'Micro' /etc/os-release && BASE="${{BASE}}micro"
            VERSION="$(grep '^\(VERSION_ID\)' /etc/os-release | sed -n 's/.*"\([[:digit:]]\+\).*/\\1/p')"
            PATCHLEVEL="$(grep '^\(VERSION_ID\)' /etc/os-release | sed -n 's/.*\.\([[:digit:]]*\).*/\\1/p')"
        fi
        Z_CLIENT_CODE_BASE="${{BASE:-unknown}}"
        Z_CLIENT_CODE_VERSION="${{VERSION:-unknown}}"
        Z_CLIENT_CODE_PATCHLEVEL="${{PATCHLEVEL:-0}}"
    }}

    function getZ_MISSING() {{
        local NEEDED="{PKG_NAME}"
        if [ $VENV_ENABLED -eq 1 ]; then
            NEEDED="{PKG_NAME_VENV}"
        fi
        if [ "$Z_CLIENT_CODE_BASE" == "sle" -a "$Z_CLIENT_CODE_VERSION" == "10" ]; then
            # (bnc#789373) Code 10 product migration requires 'xsltproc' being installed
            which 'xsltproc' || NEEDED="$NEEDED libxslt"
        fi
        Z_MISSING=""
        for P in $NEEDED; do
            rpm -q "$P" || Z_MISSING="$Z_MISSING $P"
        done
    }}

    echo "* check for necessary packages being installed..."
    # client codebase determines repo url to use and whether additional
    # preparations are needed before installing the missing packages.
    getZ_CLIENT_CODE_BASE
    echo "* client codebase is ${{Z_CLIENT_CODE_BASE}}-${{Z_CLIENT_CODE_VERSION}}-sp${{Z_CLIENT_CODE_PATCHLEVEL}}"

    CLIENT_REPOS_ROOT="${{CLIENT_REPOS_ROOT:-${{HTTPS_PUB_DIRECTORY}}/repositories}}"
    CLIENT_REPO_URL="${{CLIENT_REPOS_ROOT}}/${{Z_CLIENT_CODE_BASE}}/${{Z_CLIENT_CODE_VERSION}}/${{Z_CLIENT_CODE_PATCHLEVEL}}/bootstrap"
    CLIENT_REPO_NAME="susemanager:bootstrap"
    CLIENT_REPO_FILE="/etc/zypp/repos.d/$CLIENT_REPO_NAME.repo"
{TEST_VENV_CALL}
    getZ_MISSING

    if [ -z "$Z_MISSING" ]; then
        echo "    no packages missing."
        setup_bootstrap_repo
    else
        echo "* going to install missing packages..."

        # Note: We try to install the missing packages even if adding the repo fails.
        # Might be some other system repo provides them instead.
        
        setup_bootstrap_repo

        if [ -z "$SNAPSHOT_ID" ]; then
            zypper --non-interactive --gpg-auto-import-keys refresh "$CLIENT_REPO_NAME"
            # install missing packages
            zypper --non-interactive in $Z_MISSING
            for P in $Z_MISSING; do
                rpm -q --whatprovides "$P" || {{
                    echo "ERROR: Failed to install all missing packages."
                    exit 1
                }}
            done
        else
            call_tukit "zypper --non-interactive --gpg-auto-import-keys refresh '$CLIENT_REPO_NAME'"
            if ! call_tukit "zypper --non-interactive install $Z_MISSING"; then
                 echo "ERROR: Failed to install all required packages."
                 tukit abort "$SNAPSHOT_ID"
                 exit 1
            fi
        fi
    fi

    # try update main packages for registration from any repo which is available
    if [ $VENV_ENABLED -eq 1 ]; then
        if [ -z "$SNAPSHOT_ID" ]; then
            zypper --non-interactive up {PKG_NAME_VENV_UPDATE} ||:
        else
            call_tukit "zypper --non-interactive update {PKG_NAME_VENV_UPDATE} ||:"
        fi
    else
        if [ -z "$SNAPSHOT_ID"]; then
            zypper --non-interactive up {PKG_NAME_UPDATE} $RHNLIB_PKG ||:
        else
            call_tukit "zypper --non-interactive update {PKG_NAME_UPDATE} $RHNLIB_PKG ||:"
        fi
    fi

elif [ "$INSTALLER" == apt ]; then
    function check_deb_pkg_installed {{
        dpkg-query -W -f='${{Status}}' $1 2>/dev/null | grep -q "ok installed"
    }}

    function getA_CLIENT_CODE_BASE() {{
        local BASE=""
        local VERSION=""
        local VARIANT_ID=""

        if [ -f /etc/os-release ]; then
            BASE=$(source /etc/os-release; echo $ID)
            VERSION=$(source /etc/os-release; echo $VERSION_ID)
            VARIANT_ID=$(source /etc/os-release; echo $VARIANT_ID)
        fi
        A_CLIENT_CODE_BASE="${{BASE:-unknown}}"
        local VERCOMPS=(${{VERSION/\./ }}) # split into an array 18.04 -> (18 04)
        A_CLIENT_CODE_MAJOR_VERSION=${{VERCOMPS[0]}}
        # Ubuntu only
        if [ "${{BASE}}" == "ubuntu" ]; then
            A_CLIENT_CODE_MINOR_VERSION=$((${{VERCOMPS[1]}} + 0)) # convert "04" -> 4
        fi
        A_CLIENT_VARIANT_ID="${{VARIANT_ID:-unknown}}"
    }}

    function getA_MISSING() {{
        local NEEDED="salt-common salt-minion"
        if [ $VENV_ENABLED -eq 1 ]; then
            NEEDED="venv-salt-minion"
        elif [[ $A_CLIENT_CODE_BASE == "ubuntu" && $A_CLIENT_CODE_MAJOR_VERSION == 18 ]]; then
            # Ubuntu 18.04 needs these extra dependencies. They are not specified in
            # python3-salt because we don't maintain multiple .deb build instructions
            # and we can't add logic that adds the deps depending on which OS the .deb
            # is built for.
            NEEDED="$NEEDED python3-contextvars python3-immutables"
        fi
        A_MISSING=""
        for P in $NEEDED; do
            check_deb_pkg_installed "$P" || A_MISSING="$A_MISSING $P"
        done
    }}

    function test_deb_repo_exists() {{
        local repourl="$CLIENT_REPO_URL"

        $FETCH $repourl/dists/bootstrap/Release
        if [ ! -f "Release" ]; then
            echo "Bootstrap repo '$repourl' does not exist."
            repourl=""
            CLIENT_REPO_URL=""
        fi
        rm -f Release
    }}

    function setup_deb_bootstrap_repo() {{
        local repopath="$CLIENT_REPO_FILE"
        local repourl="$CLIENT_REPO_URL"

        test_deb_repo_exists

        if [ -n "$CLIENT_REPO_URL" ]; then
            echo " adding client software repository at $repourl"
            echo "deb [trusted=yes] $repourl bootstrap main" >"$repopath"
        fi
    }}

    echo "* check for necessary packages being installed..."
    getA_CLIENT_CODE_BASE
    if [ "${{A_CLIENT_CODE_BASE}}" == "astra" ]; then
        echo "* client codebase is ${{A_CLIENT_CODE_BASE}}-${{A_CLIENT_VARIANT_ID}}"
    else
        echo "* client codebase is ${{A_CLIENT_CODE_BASE}}-${{A_CLIENT_CODE_MAJOR_VERSION}}.${{A_CLIENT_CODE_MINOR_VERSION}}"
    fi

    CLIENT_REPOS_ROOT="${{CLIENT_REPOS_ROOT:-${{HTTPS_PUB_DIRECTORY}}/repositories}}"
    # Debian does not need minor version in the bootstrap repo URL
    if [ "${{A_CLIENT_CODE_BASE}}" == "debian" ] || [ "${{A_CLIENT_CODE_BASE}}" == "raspbian" ]; then
        CLIENT_REPO_URL="${{CLIENT_REPOS_ROOT}}/${{A_CLIENT_CODE_BASE}}/${{A_CLIENT_CODE_MAJOR_VERSION}}/bootstrap"
    elif [ "${{A_CLIENT_CODE_BASE}}" == "astra" ]; then
        CLIENT_REPO_URL="${{CLIENT_REPOS_ROOT}}/${{A_CLIENT_CODE_BASE}}/${{A_CLIENT_VARIANT_ID}}/bootstrap"
    else
        CLIENT_REPO_URL="${{CLIENT_REPOS_ROOT}}/${{A_CLIENT_CODE_BASE}}/${{A_CLIENT_CODE_MAJOR_VERSION}}/${{A_CLIENT_CODE_MINOR_VERSION}}/bootstrap"
    fi
    CLIENT_REPO_NAME="susemanager_bootstrap"
    CLIENT_REPO_FILE="/etc/apt/sources.list.d/$CLIENT_REPO_NAME.list"

    setup_deb_bootstrap_repo
{TEST_VENV_CALL}
    getA_MISSING

    apt-get --yes update

    if [ -z "$A_MISSING" ]; then
        echo "  no packages missing."
    else
        echo "* going to install missing packages..."
        # check if there are any leftovers from previous salt-minion installs and purge them
        SALT_MINION_PKG="salt-minion"
        if [ $VENV_ENABLED -eq 1 ]; then
            SALT_MINION_PKG="venv-salt-minion"
        fi
        dpkg-query -W -f='${{Status}}' "$SALT_MINION_PKG" 2>/dev/null | grep -q "deinstall ok config-files"
        if [ "$?" -eq 0 ]; then
            echo "* purging previous Salt config files"
            apt-get --yes purge "$SALT_MINION_PKG"
            if [ $VENV_ENABLED -eq 1 ]; then
                rm -rf /etc/venv-salt-minion/
            else
                apt-get purge salt-common
                rm -rf /etc/salt/minion.d/
            fi
        fi
        apt-get --yes install --no-install-recommends $A_MISSING

        for P in $A_MISSING; do
            check_deb_pkg_installed "$P" || {{
            echo "ERROR: Failed to install all missing packages."
            exit 1
        }}
        done
    fi
    # try update main packages for registration from any repo which is available
    if [ $VENV_ENABLED -eq 1 ]; then
        apt-get --yes install --no-install-recommends --only-upgrade venv-salt-minion ||:
    else
        apt-get --yes install --no-install-recommends --only-upgrade salt-common salt-minion ||:
    fi

    # remove bootstrap repo
    rm -f $CLIENT_REPO_FILE

fi

remove_bootstrap_repo

""".format(PKG_NAME=' '.join(PKG_NAME), PKG_NAME_YUM=' '.join(PKG_NAME_YUM),
           PKG_NAME_UPDATE=' '.join(PKG_NAME_UPDATE),
           PKG_NAME_UPDATE_YUM=' '.join(PKG_NAME_UPDATE_YUM),
           PKG_NAME_VENV=' '.join(PKG_NAME_VENV),
           PKG_NAME_VENV_UPDATE=' '.join(PKG_NAME_VENV_UPDATE),
           PKG_NAME_VENV_UPDATE_YUM=' '.join(PKG_NAME_VENV_UPDATE_YUM),
           TEST_VENV_FUNC=TEST_VENV_FUNC, TEST_VENV_CALL=TEST_VENV_CALL)


def getGPGKeyImportSh():
    return """\
echo
echo "PREPARE GPG KEYS AND CORPORATE PUBLIC CA CERT"
echo "-------------------------------------------------"
if [ ! -z "$ORG_GPG_KEY" ]; then
    echo
    echo "* importing organizational GPG keys"
    for GPG_KEY in $(echo "$ORG_GPG_KEY" | tr "," " "); do
        rm -f ${GPG_KEY}
        $FETCH ${HTTPS_PUB_DIRECTORY}/${GPG_KEY}
        if [ "$INSTALLER" == "apt" ]; then
           apt-get --yes install --no-install-recommends gnupg
           apt-key add $GPG_KEY
        else
           rpm --import $GPG_KEY
        fi
        rm -f ${GPG_KEY}
    done
else
    echo "* no organizational GPG keys to import"
fi

"""


def getCorpCACertSh():
    return """\
echo
    if [ "$INSTALLER" == "apt" ]; then
        CERT_DIR=/usr/local/share/ca-certificates/susemanager
        TRUST_DIR=/usr/local/share/ca-certificates/susemanager
        UPDATE_TRUST_CMD="/usr/sbin/update-ca-certificates"
        ORG_CA_CERT=RHN-ORG-TRUSTED-SSL-CERT
    else
        CERT_DIR=/usr/share/rhn
        TRUST_DIR=/etc/pki/ca-trust/source/anchors
        UPDATE_TRUST_CMD="/usr/bin/update-ca-trust extract"
    fi

    if [ "$INSTALLER" == "apt" ]; then
        CERT_FILE="${ORG_CA_CERT}.crt"
    else
        CERT_FILE=${ORG_CA_CERT}
    fi

    function updateCertificates() {
        if [ -d /etc/pki/ca-trust/source/anchors  -a -x /usr/bin/update-ca-trust ]; then
            TRUST_DIR=/etc/pki/ca-trust/source/anchors
        elif [ -d /etc/pki/trust/anchors/ -a -x /usr/sbin/update-ca-certificates ]; then
            # SLE 12
            TRUST_DIR=/etc/pki/trust/anchors
            UPDATE_TRUST_CMD="/usr/sbin/update-ca-certificates"
        elif [ -d /etc/ssl/certs -a -x /usr/bin/c_rehash -a "$INSTALLER" == "zypper" ]; then
            # SLE 11
            TRUST_DIR=/etc/ssl/certs
            UPDATE_TRUST_CMD="/usr/bin/c_rehash"
            rm -f $TRUST_DIR/RHN-ORG-TRUSTED-SSL-CERT.pem
            rm -f $TRUST_DIR/RHN-ORG-TRUSTED-SSL-CERT-*.pem
            if [ -f $CERT_DIR/$CERT_FILE ]; then
                ln -sf $CERT_DIR/$CERT_FILE $TRUST_DIR/RHN-ORG-TRUSTED-SSL-CERT.pem
                if [ $(grep -- "-----BEGIN CERTIFICATE-----" $CERT_DIR/$CERT_FILE | wc -l) -gt 1 ]; then
                    csplit -b "%02d.pem" -f $TRUST_DIR/RHN-ORG-TRUSTED-SSL-CERT- $CERT_DIR/$CERT_FILE '/-----BEGIN CERTIFICATE-----/' '{*}'
                fi
            fi
            $UPDATE_TRUST_CMD >/dev/null
            return
        fi

        if [ ! -d $TRUST_DIR ]; then
            return
        fi
        if [ "$CERT_DIR" != "$TRUST_DIR" ]; then
           if [ -z "$SNAPSHOT_ID" ]; then
                if [ -f $CERT_DIR/$CERT_FILE ]; then
                    ln -sf $CERT_DIR/$CERT_FILE $TRUST_DIR
                else
                    rm -f $TRUST_DIR/$CERT_FILE
                fi
           else
               if call_tukit "test -f '$CERT_DIR/$CERT_FILE'"; then
                   call_tukit "ln -sf '$CERT_DIR/$CERT_FILE' '$TRUST_DIR'"
               else
                   call_tukit "rm -f '$TRUST_DIR/$CERT_FILE'"
               fi
            fi
        fi
        $UPDATE_TRUST_CMD
    }

    echo "* attempting to install corporate public CA cert"

    ### Check for Dynamic CA-Trust Updates - applies to RedHat and SLE-ES systems ###
    if [ -x /usr/bin/update-ca-trust ]; then
        if [ "$(/usr/bin/update-ca-trust check | grep 'PEM/JAVA Status: DISABLED')" != "" ]; then
            echo "ERROR: Dynamic CA-Trust > Updates are disabled. Enable Dynamic CA-Trust Updates with '/usr/bin/update-ca-trust force-enable'"
            echo "Finally, restart the onboarding sequence."
            exit 1
        fi
    fi

    rm -f ${ORG_CA_CERT}
    $FETCH ${HTTPS_PUB_DIRECTORY}/${ORG_CA_CERT}

    if [ -n "$SNAPSHOT_ID" ]; then
        # we need to copy certificate to the trustroot outside of transaction for zypper
        cp "$ORG_CA_CERT" /etc/pki/trust/anchors/
        call_tukit "test -d '$CERT_DIR' || mkdir -p '$CERT_DIR'"
        call_tukit "mv '/root/$ORG_CA_CERT' '$CERT_DIR'"
    else
        test -d "$CERT_DIR" || mkdir -p "$CERT_DIR"
        mv "$ORG_CA_CERT" "$CERT_DIR"
    fi
    echo "* update certificates"
    updateCertificates
"""

def getRegistrationSaltSh(productName):
    return """\
echo
echo "REGISTRATION"
echo "------------"
# Should have created an activation key or keys on the {productName}'s
# website and edited the value of ACTIVATION_KEYS above.
#
# If you require use of several different activation keys, copy this file and
# change the string as needed.
#

if [[ $ACTIVATION_KEYS =~ , ]]; then
    echo "*** ERROR: Multiple activation keys are not supported with salt!"
    exit 1
fi

MINION_ID_FILE="/etc/salt/minion_id"
SUSEMANAGER_MASTER_FILE="/etc/salt/minion.d/susemanager.conf"
MINION_SERVICE="salt-minion"

if [ $VENV_ENABLED -eq 1 ]; then
    MINION_ID_FILE="/etc/venv-salt-minion/minion_id"
    SUSEMANAGER_MASTER_FILE="/etc/venv-salt-minion/minion.d/susemanager.conf"
    MINION_SERVICE="venv-salt-minion"
fi

if [ $REGISTER_THIS_BOX -eq 1 ]; then
    echo "* registering"

    echo "$MYNAME" > "$MINION_ID_FILE"
    cat <<EOF > "$SUSEMANAGER_MASTER_FILE"
master: $HOSTNAME
server_id_use_crc: adler32
enable_legacy_startup_events: False
enable_fqdns_grains: False
start_event_grains: [machine_id, saltboot_initrd, susemanager]
mine_enabled: False
EOF
    cat <<EOF >> "$SUSEMANAGER_MASTER_FILE"

grains:
    susemanager:
EOF
    if [ -n "$ACTIVATION_KEYS" ]; then
        echo "Using activation key: \"$ACTIVATION_KEYS\""
        cat <<EOF >>"$SUSEMANAGER_MASTER_FILE"
        activation_key: "$(echo $ACTIVATION_KEYS | cut -d, -f1)"
EOF
    fi
    if [ -n "$REACTIVATION_KEY" ]; then
        echo "Using reactivation key: \"$REACTIVATION_KEY\""
        cat <<EOF >>"$SUSEMANAGER_MASTER_FILE"
        management_key: "$(echo $REACTIVATION_KEY)"
EOF
    fi
    if [ -n "$PROFILE_NAME" ]; then
        echo "Setting profile name to: $PROFILE_NAME"
        cat <<EOF >>"$SUSEMANAGER_MASTER_FILE"
        profile_name: "$(echo $PROFILE_NAME)"
EOF
    fi
    cat <<EOF >> "$SUSEMANAGER_MASTER_FILE"

system-environment:
  modules:
    pkg:
      _:
        SALT_RUNNING: 1
EOF
fi

echo "* removing TLS certificate used for bootstrap"
echo "  (will be re-added via salt state)"

removeTLSCertificate

echo "* starting salt daemon and enabling it during boot"

if [ -n "$SNAPSHOT_ID" ]; then
    call_tukit "systemctl enable '$MINION_SERVICE'"
    tukit close $SNAPSHOT_ID
    if [ "$SCHEDULE_REBOOT_AFTER_TRANSACTION" -eq 1 ]; then
        transactional-update reboot
    else
       echo "** Reboot system to apply changes"
    fi
elif [ -f /usr/lib/systemd/system/$MINION_SERVICE.service ] || [ -f /lib/systemd/system/$MINION_SERVICE.service ]; then
    systemctl enable $MINION_SERVICE
    systemctl restart $MINION_SERVICE
else
    /etc/init.d/$MINION_SERVICE restart
    /sbin/chkconfig --add $MINION_SERVICE
fi
echo "-bootstrap complete-"
""".format(productName=productName)


def removeTLSCertificate():
    """
    This method adds bash instructions to the bootstrap script to correctly
    remove TLS certificate used to install salt packages to bootstrap the
    minion.
    Since TLS certificates will be installed again with a Salt state during
    onboarding, this is required to avoid duplicates in TLS certificates.
    """

    return """\
function removeTLSCertificate() {
    if [ "$INSTALLER" == "apt" ]; then
        CERT_DIR=/usr/local/share/ca-certificates/susemanager
        TRUST_DIR=/usr/local/share/ca-certificates/susemanager
        UPDATE_TRUST_CMD="/usr/sbin/update-ca-certificates"
        ORG_CA_CERT=RHN-ORG-TRUSTED-SSL-CERT
    else
        CERT_DIR=/usr/share/rhn
        TRUST_DIR=/etc/pki/ca-trust/source/anchors
        UPDATE_TRUST_CMD="/usr/bin/update-ca-trust extract"
    fi

    if [ -f /usr/share/rhn/${ORG_CA_CERT} ]; then
        CERT_FILE=${ORG_CA_CERT}
        rm -f /usr/share/rhn/${ORG_CA_CERT}
    elif [ -f /usr/local/share/ca-certificates/susemanager/${ORG_CA_CERT}.crt ]; then
        CERT_FILE=${ORG_CA_CERT}.crt
        rm -f /usr/local/share/ca-certificates/susemanager/${CERT_FILE}
    fi
    updateCertificates
}

"""
