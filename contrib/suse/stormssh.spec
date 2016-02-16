#
# spec file for package python-stormssh
#
# Copyright (c) 2014 SUSE LINUX Products GmbH, Nuernberg, Germany.
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via http://bugs.opensuse.org/


Name:           python-stormssh
Version:        0.6.4
Release:        0
License:        MIT
Summary:        Management commands to ssh config files
Url:            http://github.com/emre/storm
Group:          Development/Languages/Python
Source:         https://pypi.python.org/packages/source/s/stormssh/stormssh-%{version}.tar.gz
BuildRequires:  python-devel
BuildRequires:  python-setuptools
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
%if 0%{?suse_version} && 0%{?suse_version} <= 1110
%{!?python_sitelib: %global python_sitelib %(python -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%else
BuildArch:      noarch
%endif

%description
Manage your SSH like a boss

%prep
%setup -q -n stormssh-%{version}

%build
python setup.py build

%install
python setup.py install --prefix=%{_prefix} --root=%{buildroot}

%files
%defattr(-,root,root,-)
%{python_sitelib}/*
%{_prefix}/bin/storm


%changelog
-------------------------------------------------------------------
Tue Jul 22 11:42:58 UTC 2014 - lowks@lowkster.com

- 
Adding stormssh package
