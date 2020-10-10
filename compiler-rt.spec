%global crt_srcdir compiler-rt-%{version}%{?rc_ver:rc%{rc_ver}}.src
%global optflags %(echo %{optflags} -D_DEFAULT_SOURCE)
%global optflags %(echo %{optflags} -Dasm=__asm__)

Name:		compiler-rt
Version:	10.0.1
Release:	1
Summary:	LLVM "compiler-rt" runtime libraries
License:	NCSA or MIT
URL:		http://llvm.org
Source0:	https://github.com/llvm/llvm-project/releases/download/llvmorg-%{version}/%{crt_srcdir}.tar.xz
Patch0000:	0001-PATCH-std-thread-copy.patch

BuildRequires:	gcc
BuildRequires:	gcc-c++
BuildRequires:	cmake
BuildRequires:	python3
# We need python3-devel for pathfix.py.
BuildRequires:	python3-devel
BuildRequires:	llvm-devel = %{version}
BuildRequires:	llvm-static = %{version}

%description
The compiler-rt project is a part of the LLVM project. It provides
implementation of the low-level target-specific hooks required by
code generation, sanitizer runtimes and profiling library for code
instrumentation, and Blocks C language extension.

%prep
%autosetup -n %{crt_srcdir} -p1

pathfix.py -i %{__python3} -pn lib/hwasan/scripts/hwasan_symbolize

%build
mkdir -p _build
cd _build
%cmake .. \
	-DCMAKE_BUILD_TYPE=RelWithDebInfo \
	-DLLVM_CONFIG_PATH:FILEPATH=%{_bindir}/llvm-config-%{__isa_bits} \
	\
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
mkdir -p %{buildroot}%{_libdir}/clang/%{version}/share
mv -v %{buildroot}%{_datadir}/*list.txt  %{buildroot}%{_libdir}/clang/%{version}/share/

# move sanitizer libs to better place
%global libclang_rt_installdir lib/linux
mkdir -p %{buildroot}%{_libdir}/clang/%{version}/lib
mv -v %{buildroot}%{_prefix}/%{libclang_rt_installdir}/*clang_rt* %{buildroot}%{_libdir}/clang/%{version}/lib
mkdir -p %{buildroot}%{_libdir}/clang/%{version}/lib/linux/
pushd %{buildroot}%{_libdir}/clang/%{version}/lib
for i in *.a *.so
do
	ln -s ../$i linux/$i
done
popd

%ifarch %{ix86}
%post
if test "`uname -m`" = x86_64
then
	cd %{_libdir}/clang/%{version}/lib
	mkdir -p ../../../../lib64/clang/%{version}/lib
	for i in *.a *.so
	do
		ln -s ../../../../%{_lib}/clang/%{version}/lib/$i ../../../../lib64/clang/%{version}/lib/$i
	done
fi

%preun

if test "`uname -m`" = x86_64
then
	cd %{_libdir}/clang/%{version}/lib
	for i in *.a *.so
	do
		rm ../../../../lib64/clang/%{version}/lib/$i
	done
	rmdir -p ../../../../lib64/clang/%{version}/lib 2>/dev/null 1>/dev/null || :
fi

%endif

%check
#make check-all -C _build

%files
%{_includedir}/*
%{_libdir}/clang/%{version}
%ifarch x86_64 aarch64
%{_bindir}/hwasan_symbolize
%endif

%changelog
* Thu Sep 30 2020 Jeffery.Gao <gaojianxing@huawei.com> - 10.0.1-1
- Update to 10.0.1

* Thu Dec 5 2019 openEuler Buildteam <buildteam@openeuler.org> - 7.0.0-2
- Package init
