%global libclang_rt_installdir lib/linux
%global crt_srcdir compiler-rt-%{version}.src
%global debug_package %{nil}

Name:           compiler-rt
Version:        8.0.1
Release:        1%{?dist}
Summary:        LLVM "compiler-rt" runtime libraries
License:        NCSA or MIT
URL:            http://llvm.org
Source0:        https://github.com/llvm/llvm-project/releases/download/llvmorg-%{version}/%{crt_srcdir}.tar.xz
Patch0000:      0001-ipc_perm.patch


BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  python3

%description
The compiler-rt project is a part of the LLVM project. It provides
implementation of the low-level target-specific hooks required by
code generation, sanitizer runtimes and profiling library for code
instrumentation, and Blocks C language extension.

%prep
%autosetup -n %{crt_srcdir} -p1

%build
mkdir -p _build
cd _build
%cmake \
        -DCMAKE_BUILD_TYPE=RelWithDebInfo \
        -DCMAKE_C_COMPILER_TARGET=%{_arch} \
        -DCOMPILER_RT_DEFAULT_TARGET_ONLY=ON \
%if 0%{?__isa_bits} == 64
        -DLLVM_LIBDIR_SUFFIX=64 \
%else
        -DLLVM_LIBDIR_SUFFIX= \
%endif
  ..

%make_build

%install
cd _build
%make_install

mkdir -p %{buildroot}%{_libdir}/clang/%{version}/share
for file in asan_blacklist.txt msan_blacklist.txt dfsan_abilist.txt cfi_blacklist.txt hwasan_blacklist.txt; do
    mv -v %{buildroot}%{_datadir}/${file}  %{buildroot}%{_libdir}/clang/%{version}/share/
done

# move sanitizer libs to better place
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


%files
%{_includedir}/*
%{_libdir}/clang/%{version}