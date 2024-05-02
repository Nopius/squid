Name:     squid69
Version:  6.9
Release:  1%{?dist}
Summary:  The Squid proxy caching server
Epoch:    7
# We need Epoch: 7 because squid 3.5 has Epoch 7 and firewall and filesysytem 
#                packages depend on this version
# See CREDITS for breakdown of non GPLv2+ code
License:  GPLv2+ and (LGPLv2+ and MIT and BSD and Public Domain)
Group:    System Environment/Daemons
URL:      http://www.squid-cache.org
Source0:  https://www.squid-cache.org/Versions/v%{epoch}/squid-%{version}.tar.gz
Source2:  squid.logrotate
Source3:  squid.sysconfig
%if %{defined systemd_requires}
Patch0:  squid-6.9.1-systemd-service.patch
Source6: squid.nm
%endif
Source5:  squid.pam


Buildroot: %{_tmppath}/squid-%{version}-%{release}-root-%(%{__id_u} -n)
Requires: bash >= 2.0
Requires(pre): shadow-utils
Requires(post): /sbin/chkconfig
Requires(preun): /sbin/chkconfig
%if %{defined systemd_requires}
Requires(post): systemd
Requires(preun): systemd 
Requires(postun): systemd
%endif
# squid_pam_auth requires PAM development libs
BuildRequires: pam-devel
# SSL support requires OpenSSL
BuildRequires: openssl-devel
BuildRequires: scl-utils devtoolset-11-runtime
# 
BuildRequires: libtool libtool-ltdl-devel
# For test suite
BuildRequires: pkgconfig
BuildRequires: autoconf

%description
Squid is a high-performance proxy caching server for Web clients,
supporting FTP, gopher, and HTTP data objects. Unlike traditional
caching software, Squid handles all requests in a single,
non-blocking, I/O-driven process. Squid keeps meta data and especially
hot objects cached in RAM, caches DNS lookups, supports non-blocking
DNS lookups, and implements negative caching of failed requests.

Squid consists of a main server program squid, a Domain Name System
lookup program (dnsserver), a program for retrieving FTP data
(ftpget), and some management and client tools.

%prep
%setup -q -n squid-%{version}

%if %{defined systemd_requires}
%patch0
%endif

%build
%global scl scl enable devtoolset-11 --
%global make_build %{scl} %{make_build}
%global make_install %{scl} %{make_install}

%scl ./bootstrap.sh

%ifarch x86_64
export CXXFLAGS="$RPM_OPT_FLAGS -fPIC -march=x86-64"
export CFLAGS="$RPM_OPT_FLAGS -fPIC -march=x86-64"
export LDFLAGS="$RPM_LD_FLAGS -pie -Wl,-z,relro -Wl,-z,now -Wl,--warn-shared-textrel"
%endif


%scl ./configure CXXFLAGS="$CXXFLAGS" CFLAGS="$CFLAGS" LDFLAGS="$LDFLAGS" \
  --prefix=%{_prefix} \
  --includedir=%{_includedir} \
  --datadir=%{_datarootdir}/squid \
  --bindir=%{_sbindir} \
  --mandir=%{_mandir} \
  --libexecdir=%{_libexecdir}/squid \
  --localstatedir=%{_localstatedir} \
  --sysconfdir=%{_sysconfdir}/squid \
  --with-logdir=%{_localstatedir}/log/squid \
  --with-pidfile=%{_localstatedir}/run/squid.pid \
  --enable-eui \
   %ifnarch %{power64} ia64 x86_64 s390x aarch64
   --with-large-files \
   %endif
  --enable-follow-x-forwarded-for \
  --enable-auth \
  --enable-auth-basic=DB,NCSA,PAM,SASL,getpwnam \
  --enable-auth-digest=file \
  --enable-external-acl-helpers=file_userip,session,unix_group,wbinfo_group \
  --enable-cachemgr-hostname=localhost \
  --enable-delay-pools \
  --disable-ident-lookups \
  --enable-linux-netfilter \
  --enable-removal-policies=heap,lru \
  --with-openssl \
  --enable-ssl-crtd \
  --enable-storeio=aufs,diskd,rock,ufs \
  --with-default-user=squid \
  --disable-arch-native \
  --enable-forw-via-db \
  --enable-x-accelerator-vary 


%make_build DEFAULT_SWAP_DIR=%{_localstatedir}/spool/squid CXXFLAGS="$CXXFLAGS" CFLAGS="$CFLAGS" LDFLAGS="$LDFLAGS" 

%check
%make_build check


%install
rm -rf $RPM_BUILD_ROOT
%scl %make_install

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d
install -m 644 %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/squid

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig
install -m 644 %{SOURCE3} $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/squid

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/pam.d
install -m 644 %{SOURCE5} $RPM_BUILD_ROOT%{_sysconfdir}/pam.d/squid

mkdir -p $RPM_BUILD_ROOT%{_libexecdir}/squid


%if %{defined systemd_requires}
mkdir -p $RPM_BUILD_ROOT%{_unitdir}
install -m 644 tools/systemd/squid.service  $RPM_BUILD_ROOT%{_unitdir}

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/NetworkManager/dispatcher.d
install -m 644 %{SOURCE6} $RPM_BUILD_ROOT%{_sysconfdir}/NetworkManager/dispatcher.d/20-squid

%else
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/rc.d/init.d
install -m 755 tools/sysvinit/squid.rc $RPM_BUILD_ROOT%{_sysconfdir}/rc.d/init.d/squid
%endif

mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/log/squid
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/spool/squid
chmod 644 contrib/url-normalizer.pl contrib/user-agents.pl
iconv -f ISO88591 -t UTF8 ChangeLog -o ChangeLog.tmp
mv -f ChangeLog.tmp ChangeLog

# Move the MIB definition to the proper place (and name)
mkdir -p $RPM_BUILD_ROOT/%{_datarootdir}/squid/snmp/mibs
mv $RPM_BUILD_ROOT/%{_datarootdir}/squid/mib.txt $RPM_BUILD_ROOT/%{_datarootdir}/squid/snmp/mibs/SQUID-MIB.txt

# squid.conf.documented is documentation. We ship that in doc/
rm -f $RPM_BUILD_ROOT%{_sysconfdir}/squid/squid.conf.documented

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%doc COPYING 
%doc CONTRIBUTORS README ChangeLog QUICKSTART src/squid.conf.documented
#%doc contrib/url-normalizer.pl contrib/user-agents.pl

%if %{defined systemd_requires}
%attr(755,root,root) %{_unitdir}/squid.service
%else
%attr(755,root,root) %{_sysconfdir}/rc.d/init.d/squid
%endif

%attr(755,root,root) %dir %{_libexecdir}/squid
%attr(755,root,root) %dir %{_sysconfdir}/squid
%attr(750,squid,squid) %dir %{_localstatedir}/log/squid
%attr(750,squid,squid) %dir %{_localstatedir}/spool/squid

%config(noreplace) %attr(640,root,squid) %{_sysconfdir}/squid/squid.conf
%config(noreplace) %attr(644,root,squid) %{_sysconfdir}/squid/cachemgr.conf
%config(noreplace) %{_sysconfdir}/squid/mime.conf
%config(noreplace) %{_sysconfdir}/squid/errorpage.css
%config(noreplace) %{_sysconfdir}/sysconfig/squid
# These are not noreplace because they are just sample config files
%config %{_sysconfdir}/squid/squid.conf.default
%config %{_sysconfdir}/squid/mime.conf.default
%config %{_sysconfdir}/squid/errorpage.css.default
%config %{_sysconfdir}/squid/cachemgr.conf.default
%config(noreplace) %{_sysconfdir}/pam.d/squid
%config(noreplace) %{_sysconfdir}/logrotate.d/squid

%dir %{_datadir}/squid
%attr(-,root,root) %{_datadir}/squid/errors
%if %{defined systemd_requires}
%attr(755,root,root) %{_sysconfdir}/NetworkManager/dispatcher.d/20-squid
%endif

%{_sbindir}/squid
%{_sbindir}/squidclient
%{_sbindir}/purge
%{_mandir}/man8/*
%{_mandir}/man1/*
%{_datadir}/squid/snmp/mibs/SQUID-MIB.txt
%{_libexecdir}/squid
%{_datadir}/squid/icons
%{_unitdir}/squid.service

%pre
if ! getent group squid >/dev/null 2>&1; then
  /usr/sbin/groupadd -g 23 squid
fi

if ! getent passwd squid >/dev/null 2>&1 ; then
  /usr/sbin/useradd -g 23 -u 23 -d %{_localstatedir}/spool/squid -r -s /sbin/nologin squid >/dev/null 2>&1 || exit 1 
fi

for i in %{_localstatedir}/log/squid %{_localstatedir}/spool/squid ; do
        if [ -d $i ] ; then
                for adir in `find $i -maxdepth 0 \! -user squid`; do
                        chown -R squid:squid $adir
                done
        fi
done

exit 0

%post
%if %{defined systemd_requires}
%systemd_post squid.service
%endif

%preun
%if %{defined systemd_requires}
%systemd_preun squid.service
%endif

%postun
%if %{defined systemd_requires}
%systemd_postun_with_restart squid.service
%endif


%changelog
* Fri Apr 26 2024 Artyom A. Konovalenko <nopius@nopius.com> - 6:6.9
- new version 6.9
- make working on RHEL 7 with scl

