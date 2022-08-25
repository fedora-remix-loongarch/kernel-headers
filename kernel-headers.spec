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
%define base_sublevel 19

## If this is a released kernel ##
%if 0%{?released_kernel}

# Do we have a -stable update to apply?
%define stable_update 4
# Set rpm version accordingly
%if 0%{?stable_update}
%define stablerev %{stable_update}
%define stable_base %{stable_update}
%endif
%define rpmversion 5.%{base_sublevel}.%{stable_update}

## The not-released-kernel case ##
%else
# The next upstream release sublevel (base_sublevel+1)
%define upstream_sublevel %(echo $((%{base_sublevel} + 1)))
# The rc snapshot level
%global rcrev 0
# The git snapshot level
%define gitrev 0
# Set rpm version accordingly
%define rpmversion 5.%{upstream_sublevel}.0
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
Source0: kernel-headers-%{rpmversion}.tar.xz
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
ARCH_LIST="arm arm64 powerpc riscv s390 x86"

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
	riscv64)
		ARCH=riscv
		;;
	s390x)
		ARCH=s390
		;;
	x86_64|i*86)
		ARCH=x86
		;;
esac

cd arch-$ARCH/include
mkdir -p $RPM_BUILD_ROOT%{_includedir}
cp -a asm-generic $RPM_BUILD_ROOT%{_includedir}

# Copy all the architectures we care about to their respective asm directories
for arch in $ARCH_LIST; do
	mkdir -p $RPM_BUILD_ROOT%{_prefix}/${arch}-linux-gnu/include
	cp -a asm-generic $RPM_BUILD_ROOT%{_prefix}/${arch}-linux-gnu/include/
done

# Remove what we copied already
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
* Thu Aug 25 2022 Justin M. Forbes <jforbes@fedoraproject.org> - 5.19.4-200
- Linux v5.19.4

* Fri Jul 22 2022 Justin M. Forbes <jforbes@fedoraproject.org> - 5.18.13-200
- Linux v5.18.13

* Tue Jun 14 2022 Justin M. Forbes <jforbes@fedoraproject.org> - 5.18.4-200
- Linux v5.18.4

* Wed May 25 2022 Justin M. Forbes <jforbes@fedoraproject.org> - 5.17.11-300
- Linux v5.17.11

* Mon May 09 2022 Justin M. Forbes <jforbes@fedoraproject.org> - 5.17.6-300
- Linux v5.17.6

* Wed Apr 20 2022 Justin M. Forbes <jforbes@fedoraproject.org> - 5.17.4-300
- Linux v5.17.4

* Thu Mar 24 2022 Justin M. Forbes <jforbes@fedoraproject.org>- 5.17.0-300
- Linux v5.17.0

* Mon Mar 14 2022 Justin M. Forbes <jforbes@fedoraproject.org> - 5.17.0-0.rc8.git0.1
- Linux v5.17-rc8.git0

* Mon Mar 07 2022 Justin M. Forbes <jforbes@fedoraproject.org> - 5.17.0-0.rc7.git0.1
- Linux v5.17-rc7.git0

* Mon Feb 28 2022 Justin M. Forbes <jforbes@fedoraproject.org> - 5.17.0-0.rc6.git0.1
- Linux v5.17-rc6.git0

* Mon Feb 21 2022 Justin M. Forbes <jforbes@fedoraproject.org> - 5.17.0-0.rc5.git0.1
- Linux v5.17-rc5.git0

* Mon Feb 14 2022 Justin M. Forbes <jforbes@fedoraproject.org> - 5.17.0-0.rc4.git0.1
- Linux v5.17-rc4.git0

* Mon Feb 07 2022 Justin M. Forbes <jforbes@fedoraproject.org> - 5.17.0-0.rc3.git0.1
- Linux v5.17-rc3.git0

* Sun Jan 30 2022 Justin M. Forbes <jforbes@fedoraproject.org> - 5.17.0-0.rc2.git0.1
- Linux v5.17-rc2.git0

* Mon Jan 24 2022 Justin M. Forbes <jforbes@fedoraproject.org> - 5.17.0-0.rc1.git0.1
- Linux v5.17-rc1.git0

* Thu Jan 20 2022 Fedora Release Engineering <releng@fedoraproject.org> - 5.16.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_36_Mass_Rebuild

* Mon Jan 10 2022 Justin M. Forbes <jforbes@fedoraproject.org> - 5.16.0-1
- Linux v5.16

* Mon Jan 03 2022 Justin M. Forbes <jforbes@fedoraproject.org> - 5.16.0-0.rc8.git0.1
- Linux v5.16-rc8.git0

* Mon Dec 27 2021 Justin M. Forbes <jforbes@fedoraproject.org> - 5.16.0-0.rc7.git0.1
- Linux v5.16-rc7.git0

* Mon Dec 20 2021 Justin M. Forbes <jforbes@fedoraproject.org> - 5.16.0-0.rc6.git0.1
- Linux v5.16-rc6.git0

* Mon Dec 13 2021 Justin M. Forbes <jforbes@fedoraproject.org> - 5.16.0-0.rc5.git0.1
- Linux v5.16-rc5.git0

* Mon Dec 06 2021 Justin M. Forbes <jforbes@fedoraproject.org> - 5.16.0-0.rc4.git0.1
- Linux v5.16-rc4.git0

* Mon Nov 15 2021 Justin M. Forbes <jforbes@fedoraproject.org> - 5.16.0-0.rc1.git0.1
- Linux v5.16-rc1.git0

* Mon Nov 01 2021 Justin M. Forbes <jforbes@fedoraproject.org> - 5.15.0-1
- Linux v5.15.0

* Tue Oct 26 2021 Justin M. Forbes <jforbes@fedoraproject.org> - 5.15.0-0.rc7.git0.1
- Linux v5.15-rc7.git0

* Mon Oct 18 2021 Justin M. Forbes <jforbes@fedoraproject.org> - 5.15.0-0.rc6.git0.1
- Linux v5.15-rc6.git0

* Mon Oct 11 2021 Justin M. Forbes <jforbes@fedoraproject.org> - 5.15.0-0.rc5.git0.1
- Linux v5.15-rc5.git0

* Mon Oct 04 2021 Justin M. Forbes <jforbes@fedoraproject.org> - 5.15.0-0.rc4.git0.1
- Linux v5.15-rc4.git0

* Mon Sep 20 2021 Justin M. Forbes <jforbes@fedoraproject.org> - 5.15.0-0.rc2.git0.1
- Linux v5.15-rc2.git0

* Mon Sep 13 2021 Justin M. Forbes <jforbes@fedoraproject.org> - 5.15.0-0.rc1.git0.1
- Linux v5.15-rc1.git0
