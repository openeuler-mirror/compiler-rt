%global crt_srcdir compiler-rt-%{version}%{?rc_ver:rc%{rc_ver}}.src

Name:           compiler-rt
Version:        7.0.0
Release:        3
Summary:        LLVM "compiler-rt" runtime libraries
License:        NCSA or MIT
URL:            http://llvm.org
Source0:        http://llvm.org/releases/%{version}/%{crt_srcdir}.tar.xz
BuildRequires:  gcc gcc-c++ cmake python3 python3-devel
BuildRequires:  llvm-devel = %{version} llvm-static = %{version}

%description
The compiler-rt project provides highly tuned implementations of the
low-level code generator support routines like "__fixunsdfdi" and other
calls generated when a target doesn't have a short sequence of native
instructions to implement a core IR operation.

%prep
%autosetup -n %{crt_srcdir} -p1
pathfix.py -i %{__python3} -pn .

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
    -DCOMPILER_RT_INCLUDE_TESTS:BOOL=OFF

%make_build

%install
cd _build
%make_install

mkdir -p %{buildroot}%{_libdir}/clang/%{version}/lib

%ifarch aarch64
%global aarch64_blacklists hwasan_blacklist.txt
%endif

for file in %{aarch64_blacklists} asan_blacklist.txt msan_blacklist.txt dfsan_blacklist.txt \
    cfi_blacklist.txt dfsan_abilist.txt hwasan_blacklist.txt; do
    mv -v %{buildroot}%{_datadir}/${file} %{buildroot}%{_libdir}/clang/%{version}/ || :
done

mv -v %{buildroot}%{_prefix}/lib/linux/libclang_rt* %{buildroot}%{_libdir}/clang/%{version}/lib
mkdir -p %{buildroot}%{_libdir}/clang/%{version}/lib/linux/
pushd %{buildroot}%{_libdir}/clang/%{version}/lib
for i in *.a *.syms *.so; do
    ln -s ../$i linux/$i
done

%check
cd _build

%files
%defattr(-,root,root)
%license LICENSE.TXT
%{_includedir}/*
%{_libdir}/clang/%{version}

%changelog
* Tue Nov 03 2020 Jeffery.Gao <gaojianxing@huawei.com> - 7.0.0-3
- reback to 7.0.0 because nodejs upgrade after openEuler update.

* Thu Sep 30 2020 Jeffery.Gao <gaojianxing@huawei.com> - 10.0.1-1
- Upgrade to 10.1

* Thu Dec 5 2019 openEuler Buildteam <buildteam@openeuler.org> - 7.0.0-2
- Package init
