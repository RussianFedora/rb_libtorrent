Name:		rb_libtorrent
Version:	0.15.7
Release:	1%{?dist}.R

Summary:	A C++ BitTorrent library aiming to be the best alternative
Group:		System Environment/Libraries
License:	BSD
URL:		http://www.rasterbar.com/products/libtorrent/
Source0:	http://libtorrent.googlecode.com/files/libtorrent-rasterbar-%{version}.tar.gz
%define		Source0_sha1sum 5ddc5966436f98c146b6aba8595dfe86cecb6724
Source1:	%{name}-README-renames.Fedora
Source2:	%{name}-COPYING.Boost
Source3:	%{name}-COPYING.zlib
BuildRequires:	boost-devel
BuildRequires:	libtool
BuildRequires:	python-devel
BuildRequires:	python-setuptools
BuildRequires:	zlib-devel
# Necessary for 'rename'...
BuildRequires:	util-linux-ng
BuildRequires:	openssl-devel


%description
%{name} is a C++ library that aims to be a good alternative to all
the other BitTorrent implementations around. It is a library and not a full
featured client, although it comes with a few working example clients.

Its main goals are to be very efficient (in terms of CPU and memory usage) as
well as being very easy to use both as a user and developer. 


%package 	devel
Summary:	Development files for %{name}
Group:		Development/Libraries
License:	BSD and zlib and Boost
Requires:	%{name} = %{version}-%{release}
Requires:	pkgconfig
# FIXME: Same include directory. :(
Conflicts:	libtorrent-devel
# Needed for various headers used via #include directives...
Requires:	boost-devel
Requires:	openssl-devel


%description	devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.

The various source and header files included in this package are licensed
under the revised BSD, zlib/libpng, and Boost Public licenses. See the various
COPYING files in the included documentation for the full text of these
licenses, as well as the comments blocks in the source code for which license
a given source or header file is released under.


%package	examples
Summary:	Example clients using %{name}
Group:		Applications/Internet
License:	BSD
Requires:	%{name} = %{version}-%{release}


%description	examples
The %{name}-examples package contains example clients which intend to
show how to make use of its various features. (Due to potential
namespace conflicts, a couple of the examples had to be renamed. See the
included documentation for more details.)


%package	python
Summary:	Python bindings for %{name}
Group:		Development/Languages
License:	Boost
Requires:	%{name} = %{version}-%{release}


%description	python
The %{name}-python package contains Python language bindings (the
'libtorrent' module) that allow it to be used from within Python applications.


%prep
%setup -q -n "libtorrent-rasterbar-%{version}"
# Ensure that we get the licenses installed appropriately.
install -p -m 0644 COPYING COPYING.BSD
install -p -m 0644 %{SOURCE2} COPYING.Boost
install -p -m 0644 %{SOURCE3} COPYING.zlib
# Finally, ensure that everything is UTF-8, as it should be.
iconv -t UTF-8 -f ISO_8859-15 AUTHORS -o AUTHORS.iconv
mv AUTHORS.iconv AUTHORS
# Fix the interpreter for the example clients
sed -i -e 's:^#!/bin/python$:#!/usr/bin/python:' bindings/python/{simple_,}client.py
# safer and less side-effects than using LIBTOOL=/usr/bin/libtool -- Rex
# else, can use the autoreconf -i hammer
%if "%{_libdir}" != "/usr/lib"
sed -i -e 's|"/lib /usr/lib|"/%{_lib} %{_libdir}|' configure
%endif
# Use boost filesystem 2 explicitly (bug 654807)
sed -i -e '/Cflags:/s|^\(.*\)$|\1 -DBOOST_FILESYSTEM_VERSION=2|' \
	libtorrent-rasterbar.pc.in


%build
# FIXME
# There are lots of warning about breaking aliasing rules, so
# for now compiling with -fno-strict-aliasing. Please check if
# newer version fixes this.
export CFLAGS="%{optflags} -fno-strict-aliasing"
export CXXFLAGS="%{optflags} -fno-strict-aliasing"
# Use boost filesystem 2 explicitly (bug 654807)
export CFLAGS="$CFLAGS -DBOOST_FILESYSTEM_VERSION=2"
export CXXFLAGS="$CXXFLAGS -DBOOST_FILESYSTEM_VERSION=2"
%configure \
    --enable-shared \
    --enable-static \
    --enable-encryption \
    --enable-geoip \
    --enable-examples \
    --enable-python-binding \
    --with-boost-filesystem=mt \
    --with-boost-python=mt \
    --with-boost-system=mt \
    --with-boost-thread=mt \
    --with-zlib=system
make


%check
make check


%install
rm -rf %{buildroot}
# remove useless files in docs dir
rm -f docs/*.rst docs/*.dot docs/*.graffle
# Ensure that we preserve our timestamps properly
export CPPROG="%{__cp} -p"
make install DESTDIR="%{buildroot}" INSTALL="%{__install} -c -p"
# Do the renaming due to the somewhat limited %%_bindir namespace.
rename client torrent_client %{buildroot}%{_bindir}/*
install -p -m 0644 %{SOURCE1} ./README-renames.Fedora
# Install the python binding module.
pushd bindings/python
    %{__python} setup.py install -O1 --skip-build --root %{buildroot}
popd


%clean
rm -rf %{buildroot}


%post -n %{name} -p /sbin/ldconfig


%postun -n %{name} -p /sbin/ldconfig


%files
%defattr(-,root,root,0755)
%doc AUTHORS ChangeLog COPYING COPYING.Boost COPYING.BSD COPYING.zlib README
%{_libdir}/libtorrent-rasterbar.so.6
%{_libdir}/libtorrent-rasterbar.so.6.0.0


%files	devel
%defattr(-,root,root,0755)
%doc docs/*
%{_libdir}/pkgconfig/libtorrent-rasterbar.pc
%{_includedir}/libtorrent/
%{_libdir}/libtorrent-rasterbar.so
%{_libdir}/libtorrent-rasterbar.a
%{_libdir}/libtorrent-rasterbar.la


%files examples
%defattr (-,root,root,0755)
%doc README-renames.Fedora
%{_bindir}/dump_torrent
%{_bindir}/enum_if
%{_bindir}/make_torrent
%{_bindir}/simple_torrent_client
%{_bindir}/torrent_client_test


%files	python
%defattr (-,root,root,0755)
%doc bindings/python/{simple_,}client.py
%{python_sitearch}/python_libtorrent-%{version}-py?.?.egg-info
%{python_sitearch}/libtorrent.so


%changelog
* Tue Jan 31 2012 Arkady L. Shane <ashejn@russianfedora.ru> - 0.15.7-1.R
- rebuilt

* Sat Sep 24 2011 LTN Packager <packager-el6rpms@LinuxTECH.NET> - 0.15.7-1
- new upstream release
- removed some useless files in doc-dir
- rearranged documentation in a more logical way avoiding duplicates

* Sun Jun 26 2011 LTN Packager <packager-el6rpms@LinuxTECH.NET> - 0.15.6-1.1
- imported from Fedora, cleaned up spec-file
- using included libasio and libgeoip

