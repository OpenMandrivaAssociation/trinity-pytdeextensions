%bcond clang 1

# TDE variables
%define tde_epoch 2
%if "%{?tde_version}" == ""
%define tde_version 14.1.5
%endif
%define pkg_rel 1

%define tde_pkg pytdeextensions
%define tde_prefix /opt/trinity


%undefine __brp_remove_la_files
%define dont_remove_libtool_files 1
%define _disable_rebuild_configure 1
%define _python_bytecompile_build 0

%define tarball_name %{tde_pkg}-trinity


Name:		trinity-%{tde_pkg}
Epoch:		%{tde_epoch}
Version:	0.4.0
Release:	%{?tde_version}_%{?!preversion:%{pkg_rel}}%{?preversion:0_%{preversion}}%{?dist}
Summary:	Python packages to support TDE applications (scripts)
Group:		Development/Libraries/Python
URL:		http://www.trinitydesktop.org/
#URL:		http://www.simonzone.com/software/pykdeextensions

License:	GPLv2+


Source0:	https://mirror.ppa.trinitydesktop.org/trinity/releases/R%{tde_version}/main/libraries/%{tarball_name}-%{tde_version}%{?preversion:~%{preversion}}.tar.xz

BuildRequires:	trinity-tdelibs-devel >= %{tde_version}

BuildRequires:	desktop-file-utils
BuildRequires:	gettext
BuildRequires:	autoconf automake libtool m4
%{!?with_clang:BuildRequires:	gcc-c++}

BuildRequires:	pytqt-devel >= %{?epoch:%{epoch}:}3.18.1
BuildRequires:	trinity-pytde-devel
BuildRequires:	trinity-pytqt-tools
Requires:		pytqt
Requires:		trinity-pytde

Requires:		trinity-libpythonize0 = %{?epoch:%{epoch}:}%{version}-%{release}

# SIP
BuildRequires:	sip4-tqt-devel >= 4.10.5
Requires:		sip4-tqt >= 4.10.5

# PYTHON support
%if "%{python}" == ""
%global python python3
%global __python %__python3
%global python_sitearch %{python3_sitearch}
%{!?python_sitearch:%global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
BuildRequires:	pkgconfig(python)
%endif


Obsoletes:		trinity-pykdeextensions < %{?epoch:%{epoch}:}%{version}-%{release}
Provides:		trinity-pykdeextensions = %{?epoch:%{epoch}:}%{version}-%{release}


%description
PyTDE Extensions is a collection of software and Python packages
to support the creation and installation of TDE applications.


%files
%defattr(-,root,root,-)
%doc AUTHORS ChangeLog COPYING NEWS README TODO
%{tde_prefix}/share/apps/pytdeextensions/
%{tde_prefix}/share/doc/tde/HTML/en/pytdeextensions/
%{python_sitearch}/*

##########

%package -n trinity-libpythonize0
Summary:	Python packages to support TDE applications (library)
Group:		Development/Libraries/Python

%description -n trinity-libpythonize0
PyTDE Extensions is a collection of software and Python packages
to support the creation and installation of TDE applications.

This package contains the libpythonize library files.

%files -n trinity-libpythonize0
%defattr(-,root,root,-)
%{tde_prefix}/%{_lib}/libpythonize.so.*

##########

%package -n trinity-libpythonize-devel
Summary:	Python packages to support TDE applications (development)
Group:		Development/Libraries/Python
Requires:	trinity-libpythonize0 = %{?epoch:%{epoch}:}%{version}-%{release}

Obsoletes:	trinity-libpythonize0-devel < %{?epoch:%{epoch}:}%{version}-%{release}
Provides:	trinity-libpythonize0-devel = %{?epoch:%{epoch}:}%{version}-%{release}

%description -n trinity-libpythonize-devel
PyTDE Extensions is a collection of software and Python packages
to support the creation and installation of TDE applications.

This package contains the libpythonize development files.

%files -n trinity-libpythonize-devel
%defattr(-,root,root,-)
%{tde_prefix}/include/tde/*.h
%{tde_prefix}/%{_lib}/libpythonize.la
%{tde_prefix}/%{_lib}/libpythonize.so

##########

%package devel
Summary:	Meta-package to install all pytdeextensions development files
Group:		Development/Libraries/Python
Requires:	%{name} = %{?epoch:%{epoch}:}%{version}-%{release}
Requires:	trinity-libpythonize-devel = %{?epoch:%{epoch}:}%{version}-%{release}

%description devel
This package is a meta-package to install all pytdeextensions development
files.

%files devel

%prep
%autosetup -p1 -n %{tarball_name}-%{tde_version}%{?preversion:~%{preversion}}

# Changes library directory to 'lib64'
# Also other fixes for distributions ...
for f in src/*.py; do
  %__sed -i "${f}" \
    -e "s|'pytde-dir=',None,|'pytde-dir=','%{python_sitearch}',|g" \
    -e "s|self.pytde_dir = None|self.pytde_dir = \"%{python_sitearch}\"|g" \
    -e "s|'kde-lib-dir=',None,|'kde-lib-dir=','%{tde_prefix}/%{_lib}',|g" \
    -e "s|self.kde_lib_dir = None|self.kde_lib_dir = \"%{tde_prefix}/%{_lib}\"|g" \
    -e "s|'kde-kcm-lib-dir=',None,|'kde-kcm-lib-dir=','%{tde_prefix}/%{_lib}/trinity',|g" \
    -e "s|self.kde_kcm_lib_dir = None|self.kde_kcm_lib_dir = \"%{tde_prefix}/%{_lib}/trinity\"|g" \
    -e "s|%{tde_prefix}/include/tde|%{tde_prefix}/include/tde|g" \
    -e 's|"/kde"|"/tde"|' \
    -e 's|"-I" + self.kde_inc_dir + "/tde"|"-I/opt/trinity/include"|' \
    -e "s|/usr/lib/pyshared/python\*|%{python_sitearch}|g"
done

%build
unset QTDIR QTINC QTLIB
export PATH="%{tde_prefix}/bin:${PATH}"

%__mkdir_p build
%__python ./setup.py build_libpythonize


%install
unset QTDIR QTINC QTLIB
export PATH="%{tde_prefix}/bin:${PATH}"

# Avoids 'error: byte-compiling is disabled.' on Mandriva/Mageia
# export PYTHONDONTWRITEBYTECODE=

%__python ./setup.py install \
	--root=%{buildroot} \
	--prefix=%{tde_prefix} \
	--install-clib=%{tde_prefix}/%{_lib} \
	--install-cheaders=%{tde_prefix}/include/tde \
   -v

# Removes BUILDROOT directory reference in installed files
for f in \
	%{buildroot}%{tde_prefix}/%{_lib}/libpythonize.la \
	%{buildroot}%{tde_prefix}/share/apps/pytdeextensions/app_templates/kcontrol_module/src/KcontrolModuleWidgetUI.py \
	%{buildroot}%{tde_prefix}/share/apps/pytdeextensions/app_templates/kdeutility/src/KDEUtilityDialogUI.py \
; do
	%__sed -i "${f}" -e "s|%{buildroot}||g"
:
done

# Moves PYTHON libraries to distribution directory
%__mkdir_p %{buildroot}%{python_sitearch}
%__mv -f %{buildroot}%{tde_prefix}/lib/python*/site-packages/* %{buildroot}%{python_sitearch}
%__rm -rf %{buildroot}%{tde_prefix}/lib/python*/site-packages

# Removes useless files
%__rm -rf %{?buildroot}%{tde_prefix}/%{_lib}/*.a

# Fix permissions on include files
%__chmod 644 %{?buildroot}%{tde_prefix}/include/tde/*.h

