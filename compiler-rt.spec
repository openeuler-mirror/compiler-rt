%bcond_without sys_llvm
%bcond_without check

%global maj_ver 17
%global min_ver 0
%global patch_ver 6
%global crt_version %{maj_ver}.%{min_ver}.%{patch_ver}
%global crt_srcdir compiler-rt-%{version}%{?rc_ver:rc%{rc_ver}}.src
%global optflags %(echo %{optflags} -D_DEFAULT_SOURCE)
%global optflags %(echo %{optflags} -Dasm=__asm__)

%if %{with sys_llvm}
%global pkg_name compiler-rt
%global install_prefix %{_prefix}
%global install_datadir %{_datadir}
%else
%global pkg_name compiler-rt%{maj_ver}
%global install_prefix %{_libdir}/llvm%{maj_ver}
%global install_datadir %{install_prefix}/share
%endif

%if 0%{?__isa_bits} == 64
%global install_libdir %{install_prefix}/lib64
%else
%global install_libdir %{install_prefix}/lib
%endif

Name:		%{pkg_name}
Version:	%{crt_version}
Release:	1
Summary:	LLVM "compiler-rt" runtime libraries

License:	NCSA or MIT
URL:		http://llvm.org
Source0:	https://github.com/llvm/llvm-project/releases/download/llvmorg-%{version}/%{crt_srcdir}.tar.xz
Source1:	https://github.com/llvm/llvm-project/releases/download/llvmorg-%{version}/%{crt_srcdir}.tar.xz.sig

BuildRequires:	gcc
BuildRequires:	gcc-c++
BuildRequires:	cmake
BuildRequires:	ninja-build
BuildRequires:	python3
# We need python3-devel for pathfix.py.
BuildRequires:	python3-devel

%if %{with sys_llvm}
BuildRequires:	llvm-devel = %{version}
BuildRequires:	llvm-test = %{version}
BuildRequires:  llvm-cmake-utils = %{version}
%else
BuildRequires:	llvm%{maj_ver}-devel = %{version}
BuildRequires:	llvm%{maj_ver}-test = %{version}
BuildRequires:	llvm%{maj_ver}-cmake-utils = %{version}
%endif

%description
The compiler-rt project is a part of the LLVM project. It provides
implementation of the low-level target-specific hooks required by
code generation, sanitizer runtimes and profiling library for code
instrumentation, and Blocks C language extension.

%prep
%autosetup -n %{crt_srcdir} -p2
# compiler-rt does not allow configuring LLVM_COMMON_CMAKE_UTILS.
ln -s %{install_datadir}/llvm/cmake ../cmake

pathfix.py -i %{__python3} -pn lib/hwasan/scripts/hwasan_symbolize

%build
# Copy CFLAGS into ASMFLAGS, so -fcf-protection is used when compiling assembly files.
export ASMFLAGS=$CFLAGS
mkdir -p _build
cd _build
%cmake  .. \
	-DCMAKE_BUILD_TYPE=RelWithDebInfo \
	-DCMAKE_MODULE_PATH=%{install_libdir}/cmake/llvm \
	-DCMAKE_SKIP_RPATH:BOOL=ON \
	-DCOMPILER_RT_INSTALL_PATH=%{install_libdir}/clang/%{maj_ver} \
	-DLLVM_ENABLE_PER_TARGET_RUNTIME_DIR=ON \
%if 0%{?__isa_bits} == 64
	-DLLVM_LIBDIR_SUFFIX=64 \
%else
	-DLLVM_LIBDIR_SUFFIX= \
%endif
	-DCOMPILER_RT_INCLUDE_TESTS:BOOL=OFF # could be on?

%make_build

%install
cd _build
%make_install

%check

#%%cmake_build --target check-compiler-rt

%files
%license LICENSE.TXT
%ifarch x86_64 aarch64
%{install_libdir}/clang/%{maj_ver}/bin/*
%endif
%{install_libdir}/clang/%{maj_ver}/include/*
%{install_libdir}/clang/%{maj_ver}/lib/*
%{install_libdir}/clang/%{maj_ver}/share/*
%ifarch x86_64 aarch64
%{install_libdir}/clang/%{maj_ver}/bin/hwasan_symbolize
%endif

%changelog
* Tue Dec 5 2023 zhoujing <zhoujing106@huawei.com> - 17.0.6-1
- Update to 17.0.6

* Tue Dec 20 2022 eastb233 <xiezhiheng@huawei.com> - 12.0.1-2
- Delete run path in DSO

* Mon Dec 27 2021 Chen Chen <chen_aka_jan@163.com> - 12.0.1-1
- Update to 12.0.1

* Fri Sep 25 2020 Guoshuai Sun <sunguoshuai@huawei.com> - 10.0.1-3
- hwasan_symbolize should run in python2 and python3, and python3 is default now

* Sat Sep 19 2020 Guoshuai Sun <sunguoshuai@huawei.com> - 10.0.1-2
- Keep "/usr/bin/env python" instead of /usr/bin/python3 in hwasan_symbolize

* Thu Jul 30 2020 Guoshuai Sun <sunguoshuai@huawei.com> - 10.0.1-1
- Update to 10.0.1

* Thu Dec 5 2019 openEuler Buildteam <buildteam@openeuler.org> - 7.0.0-2
- Package init