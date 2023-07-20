%bcond_with sys_llvm
%bcond_without check

%global maj_ver 12
%global min_ver 0
%global patch_ver 1

%if %{with sys_llvm}
%global pkg_name compiler-rt
%global install_prefix %{_prefix}
%else
%global pkg_name compiler-rt%{maj_ver}
%global install_prefix %{_libdir}/llvm%{maj_ver}
%endif

%global install_bindir %{install_prefix}/bin
%if 0%{?__isa_bits} == 64
%global install_libdir %{install_prefix}/lib64
%else
%global install_libdir %{install_prefix}/lib
%endif
%global install_includedir %{install_prefix}/include
%global install_sharedir %{install_prefix}/share

%global crt_version %{maj_ver}.%{min_ver}.%{patch_ver}
%global crt_srcdir compiler-rt-%{version}%{?rc_ver:rc%{rc_ver}}.src
%global optflags %(echo %{optflags} -D_DEFAULT_SOURCE)
%global optflags %(echo %{optflags} -Dasm=__asm__)

Name:		%{pkg_name}
Version:	%{crt_version}
Release:	3
Summary:	LLVM "compiler-rt" runtime libraries

License:	NCSA or MIT
URL:		http://llvm.org
Source0:	https://github.com/llvm/llvm-project/releases/download/llvmorg-%{version}/%{crt_srcdir}.tar.xz

Patch1:		0001-PATCH-compiler-rt-Workaround-libstdc-limitation-wrt..patch

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
Requires:       clang-resource-filesystem%{?isa} = %{version}
%else
BuildRequires:	llvm%{maj_ver}-devel = %{version}
BuildRequires:	llvm%{maj_ver}-test = %{version}
Requires:       clang%{maj_ver}-resource-filesystem%{?isa} = %{version}
%endif


%description
The compiler-rt project is a part of the LLVM project. It provides
implementation of the low-level target-specific hooks required by
code generation, sanitizer runtimes and profiling library for code
instrumentation, and Blocks C language extension.

%prep
%autosetup -n %{crt_srcdir} -p2
pathfix.py -i %{__python3} -pn lib/hwasan/scripts/hwasan_symbolize

%build
# Copy CFLAGS into ASMFLAGS, so -fcf-protection is used when compiling assembly files.
export ASMFLAGS=$CFLAGS
mkdir -p _build
cd _build
%cmake  .. \
	-DCMAKE_BUILD_TYPE=RelWithDebInfo \
    -DCMAKE_INSTALL_PREFIX=%{install_prefix} \
	-DCMAKE_MODULE_PATH=%{install_libdir}/cmake/llvm \
    -DLLVM_CONFIG_PATH=%{install_bindir}/llvm-config \
	-DCMAKE_SKIP_RPATH:BOOL=ON \
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


# move blacklist/abilist files to where clang expect them
mkdir -p %{buildroot}%{install_libdir}/clang/%{version}/share
mv -v %{buildroot}%{install_sharedir}/*list.txt  %{buildroot}%{install_libdir}/clang/%{version}/share/

# move sanitizer libs to better place
%global libclang_rt_installdir lib/linux
mkdir -p %{buildroot}%{install_libdir}/clang/%{version}/lib
mv -v %{buildroot}%{install_prefix}/%{libclang_rt_installdir}/*clang_rt* %{buildroot}%{install_libdir}/clang/%{version}/lib
mkdir -p %{buildroot}%{install_libdir}/clang/%{version}/lib/linux/
pushd %{buildroot}%{install_libdir}/clang/%{version}/lib
for i in *.a *.so
do
	ln -s ../$i linux/$i
done
popd

# multilib support: also create symlink from lib to lib64, fixes rhbz#1678240
# the symlinks will be dangling if the 32 bits version is not installed, but that should be fine
%ifarch %{ix86}
%post
if test "`uname -m`" = x86_64
then
	cd %{install_libdir}/clang/%{version}/lib
	mkdir -p ../../../../lib64/clang/%{version}/lib
	for i in *.a *.so
	do
		ln -s ../../../../%{_lib}/clang/%{version}/lib/$i ../../../../lib64/clang/%{version}/lib/$i
	done
fi

%preun

if test "`uname -m`" = x86_64
then
	cd %{install_libdir}/clang/%{version}/lib
	for i in *.a *.so
	do
		rm ../../../../lib64/clang/%{version}/lib/$i
	done
	rmdir -p ../../../../lib64/clang/%{version}/lib 2>/dev/null 1>/dev/null || :
fi

%endif

%check

#%%cmake_build --target check-compiler-rt

%files
%license LICENSE.TXT
%{install_includedir}/*
%{install_libdir}/clang/%{version}/lib/*
%{install_libdir}/clang/%{version}/share/*
%ifarch x86_64 aarch64
%{install_bindir}/hwasan_symbolize
%endif

%changelog
* Thu Jul 20 2023 cf0zhao <zhaochuanfeng@huawei.com> - 12.0.1-3
- Change the install path.

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
