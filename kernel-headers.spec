# For a stable, released kernel, released_kernel should be 1. For rawhide
# and/or a kernel built from an rc or git snapshot, released_kernel should
# be 0.
%global released_kernel 1

# define buildid .local

# baserelease defines which build revision of this kernel version we're
# building.  We used to call this fedora_build, but the magical name
# baserelease is matched by the rpmdev-bumpspec tool, which you should use.
#
# NOTE: baserelease must be > 0 or bad things will happen if you switch
#       to a released kernel (released version will be < rc version)
#
# For non-released -rc kernels, this will be appended after the rcX and
# gitX tags, so a 3 here would become part of release "0.rcX.gitX.3"
#
%global baserelease 200
%global fedora_build %{baserelease}

# base_sublevel is the kernel version we're starting with and patching
# on top of -- for example, 3.1-rc7-git1 starts with a 3.0 base,
# which yields a base_sublevel of 0.
%define base_sublevel 20

## If this is a released kernel ##
%if 0%{?released_kernel}

# Do we have a -stable update to apply?
%define stable_update 15
# Set rpm version accordingly
%if 0%{?stable_update}
%define stablerev %{stable_update}
%define stable_base %{stable_update}
%endif
%define rpmversion 4.%{base_sublevel}.%{stable_update}

## The not-released-kernel case ##
%else
# The next upstream release sublevel (base_sublevel+1)
%define upstream_sublevel %(echo $((%{base_sublevel} + 1)))
# The rc snapshot level
%global rcrev 0
# The git snapshot level
%define gitrev 0
# Set rpm version accordingly
%define rpmversion 4.%{upstream_sublevel}.0
%endif

# pkg_release is what we'll fill in for the rpm Release: field
%if 0%{?released_kernel}

%define srcversion %{fedora_build}%{?buildid}

%else

# non-released_kernel
%if 0%{?rcrev}
%define rctag .rc%rcrev
%else
%define rctag .rc0
%endif
%if 0%{?gitrev}
%define gittag .git%gitrev
%else
%define gittag .git0
%endif
%define srcversion 0%{?rctag}%{?gittag}.%{fedora_build}%{?buildid}

%endif

%define pkg_release %{?srcversion}%{?dist}

# This package doesn't contain any binary, thus no debuginfo package is needed
%global debug_package %{nil}

Name: kernel-headers
Summary: Header files for the Linux kernel for use by glibc
Group: Development/System
License: GPLv2
URL: http://www.kernel.org/
Version: %{rpmversion}
Release: %{pkg_release}
# This is a tarball with headers from the kernel, which should be created
# using create_headers_tarball.sh provided in the kernel source package.
# To create the tarball, you should go into a prepared/patched kernel sources
# directory, or git kernel source repository, and do eg.:
# For a RHEL package: (...)/create_headers_tarball.sh -m RHEL_RELEASE
# For a Fedora package: kernel/scripts/create_headers_tarball.sh -r <release number>
Source0: kernel-headers-%{rpmversion}-%{?srcversion}.tar.xz
Obsoletes: glibc-kernheaders < 3.0-46
Provides: glibc-kernheaders = 3.0-46
%if "0%{?variant}"
Obsoletes: kernel-headers < %{version}-%{release}
Provides: kernel-headers = %{version}-%{release}
%endif

%description
Kernel-headers includes the C header files that specify the interface
between the Linux kernel and userspace libraries and programs.  The
header files define structures and constants that are needed for
building most standard programs and are also needed for rebuilding the
glibc package.

%package -n kernel-cross-headers
Summary: Header files for the Linux kernel for use by cross-glibc
Group: Development/System

%description -n kernel-cross-headers
Kernel-cross-headers includes the C header files that specify the interface
between the Linux kernel and userspace libraries and programs.  The
header files define structures and constants that are needed for
building most standard programs and are also needed for rebuilding the
cross-glibc package.

%prep
%setup -q -c

%build

%install
# List of architectures we support and want to copy their headers
ARCH_LIST="arm arm64 powerpc s390 x86"

cd include

ARCH=%_target_cpu
case $ARCH in
	armv7hl)
		ARCH=arm
		;;
	aarch64)
		ARCH=arm64
		;;
	ppc64*)
		ARCH=powerpc
		;;
	s390x)
		ARCH=s390
		;;
	x86_64|i*86)
		ARCH=x86
		;;
esac

mkdir -p $RPM_BUILD_ROOT%{_includedir}
cp -a arch-$ARCH/asm $RPM_BUILD_ROOT%{_includedir}/
cp -a asm-generic $RPM_BUILD_ROOT%{_includedir}

# Copy all the architectures we care about to their respective asm directories
for arch in $ARCH_LIST; do
	mkdir -p $RPM_BUILD_ROOT%{_prefix}/${arch}-linux-gnu/include
	mv arch-${arch}/asm $RPM_BUILD_ROOT%{_prefix}/${arch}-linux-gnu/include/
	cp -a asm-generic $RPM_BUILD_ROOT%{_prefix}/${arch}-linux-gnu/include/
done

# Remove what we copied already
rm -rf arch-*/asm
rmdir arch-*
rm -rf asm-generic

# Copy the rest of the headers over
cp -a * $RPM_BUILD_ROOT%{_includedir}/
for arch in $ARCH_LIST; do
cp -a * $RPM_BUILD_ROOT%{_prefix}/${arch}-linux-gnu/include/
done

%files
%defattr(-,root,root)
%{_includedir}/*

%files -n kernel-cross-headers
%defattr(-,root,root)
%{_prefix}/*-linux-gnu/*

%changelog
* Mon Mar 11 2019 Justin M. Forbes <jforbes@fedoraproject.org> - 4.20.15-200
- Linux v4.20.15

* Tue Mar 05 2019 Justin M. Forbes <jforbes@fedoraproject.org> - 4.20.14-200
- Linux v4.20.14

* Wed Feb 27 2019 Justin M. Forbes <jforbes@fedoraproject.org> - 4.20.13-200
- Linux v4.20.13

* Mon Feb 25 2019 Justin M. Forbes <jforbes@fedoraproject.org> - 4.20.12-200
- Linux v4.20.12

* Wed Feb 20 2019 Justin M. Forbes <jforbes@fedoraproject.org> - 4.20.11-200
- Linux v4.20.11

* Fri Feb 15 2019 Justin M. Forbes <jforbes@fedoraproject.org> - 4.20.10-200
- Linux v4.20.10

* Tue Feb 12 2019 Justin M. Forbes <jforbes@fedoraproject.org> - 4.20.8-200
- Linux v4.20.8

* Wed Feb 06 2019 Justin M. Forbes <jforbes@fedoraproject.org> - 4.20.7-200
- Linux v4.20.7

* Thu Jan 31 2019 Justin M. Forbes <jforbes@fedoraproject.org> - 4.20.6-200
- Linux v4.20.6

* Mon Jan 28 2019 Justin M. Forbes <jforbes@fedoraproject.org> - 4.20.5-200
- Linux v4.20.5

* Wed Jan 23 2019 Justin M. Forbes <jforbes@fedoraproject.org> - 4.20.4-200
- Linux v4.20.4

* Thu Jan 17 2019 Justin M. Forbes <jforbes@fedoraproject.org> - 4.20.3-200
- Linux v4.20.3

* Mon Jan 14 2019 Jeremy Cline <jcline@redhat.com> - 4.19.15-300
- Linux v4.19.15

* Wed Jan 09 2019 Jeremy Cline <jcline@redhat.com> - 4.19.14-300
- Linux v4.19.14

* Sat Dec 29 2018 Jeremy Cline <jcline@redhat.com> - 4.19.13-300
- Linux v4.19.13

* Fri Dec 28 2018 Jeremy Cline <jcline@redhat.com> - 4.19.12-301
- Linux v4.19.12

* Thu Dec 20 2018 Jeremy Cline <jcline@redhat.com> - 4.19.11-300
- Linux v4.19.11

* Mon Dec 17 2018 Jeremy Cline <jcline@redhat.com> - 4.19.10-300
- Linux v4.19.10

* Thu Dec 13 2018 Jeremy Cline <jcline@redhat.com> - 4.19.9-300
- Linux v4.19.9

* Mon Dec 10 2018 Jeremy Cline <jcline@redhat.com> - 4.19.8-300
- Linux v4.19.8

* Wed Dec 05 2018 Jeremy Cline <jcline@redhat.com> - 4.19.7-300
- Linux v4.19.7

* Sun Dec 02 2018 Jeremy Cline <jcline@redhat.com> - 4.19.6-300
- Linux v4.19.6

* Tue Nov 27 2018 Jeremy Cline <jcline@redhat.com> - 4.19.5-300
- Linux v4.19.5

* Wed Nov 21 2018 Jeremy Cline <jcline@redhat.com> - 4.19.5-300
- Linux v4.19.3

* Wed Nov 14 2018 Jeremy Cline <jcline@redhat.com> - 4.19.2-300
- Linux v4.19.2

* Mon Nov 12 2018 Laura Abbott <labbott@redhat.com> - 4.18.18-300
- Linux v4.18.18

* Mon Nov 05 2018 Laura Abbott <labbott@redhat.com> - 4.18.17-300
- Linux v4.18.17

* Sun Oct 21 2018 Laura Abbott <labbott@redhat.com> - 4.18.16-300
- Linux v4.18.16

* Thu Oct 18 2018 Justin M. Forbes <jforbes@fedoraproject.org> - 4.18.15-300
- Linux v4.18.15

* Mon Oct 15 2018 Justin M. Forbes <jforbes@fedoraproject.org> - 4.18.14-300
- Linux v4.18.14

* Wed Oct 10 2018 Laura Abbott <labbott@redhat.com> - 4.18.13-300
- Linux v4.18.13

* Thu Oct 04 2018 Laura Abbott <labbott@redhat.com> - 4.18.12-300
- Linux v4.18.12

* Sun Sep 30 2018 Laura Abbott <labbott@redhat.com> - 4.18.11-300
- Linux v4.18.11

* Wed Sep 26 2018 Laura Abbott <labbott@redhat.com> - 4.18.10-300
- Linux v4.18.10

* Thu Sep 20 2018 Laura Abbott <labbott@redhat.com> - 4.18.9-300
- Linux v4.18.9

* Mon Sep 17 2018 Laura Abbott <labbott@redhat.com> - 4.18.8-300
- Linux v4.18.8

* Mon Sep 10 2018 Laura Abbott <labbott@redhat.com> - 4.18.7-300
- Linux v4.18.7

* Mon Aug 20 2018 Justin M. Forbes <jforbes@fedoraproject.org> - 4.18.3-1
- Linux v4.18.3

* Fri Aug 17 2018 Justin M. Forbes <jforbes@fedoraproject.org> - 4.18.1-1
- Linux v4.18.1

* Mon Aug 13 2018 Justin M. Forbes <jforbes@fedoraproject.org> - 4.18.0-1
- Linux v4.18

* Tue Jul 31 2018 Justin M. Forbes <jforbes@fedoraproject.org> - 4.18.0-0.rc7.git0.1
- Linux v4.18-rc7

* Fri Jul 27 2018 Justin M. Forbes <jforbes@fedoraproject.org> - 4.18.0-0.rc6.git3.1
- Initial package commit

* Mon Jul 23 2018 Justin M. Forbes <jforbes@fedoraproject.org> - 4.18.0-0.rc6.git0.1
- Changes and updates to fit inline with current Fedora process

* Thu Jul 12 2018 Herton R. Krzesinski <herton@redhat.com> - 4.18.0-0.rc4.2
- Initial version of splitted kernel-headers package.
