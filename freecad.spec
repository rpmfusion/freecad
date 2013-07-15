# Maintainers:  keep this list of plugins up to date
# List plugins in %%{_libdir}/freecad/lib, less '.so' and 'Gui.so', here
%global plugins Assembly Complete Drawing Fem FreeCAD Image Import Inspection Mesh MeshPart Part Points QtUnit Raytracing ReverseEngineering Robot Sketcher Start Web

# Some plugins go in the Mod folder instead of lib. Deal with those here:
%global mod_plugins Mod/PartDesign

# This revision is 0.12 final.
%global rev 1830

# Use updated cmake package on EL builds.
# Temporary workaround for cmake/boost bug:
# http://public.kitware.com/Bug/view.php?id=13446
%if 0%{?el6}
%global cmake %cmake28 -DBoost_NO_BOOST_CMAKE=ON
%endif

# Some configuration options for other environments
# rpmbuild --with=occ:  Compile using OpenCASCADE instead of OCE
%global occ %{?_with_occ: 1} %{?!_with_occ: 0}
# rpmbuild --with=bundled_zipios:  use bundled version of zipios++
%global bundled_zipios %{?_with_bundled_zipios: 1} %{?!_with_bundled_zipios: 0}
# rpmbuild --with=bundled_pycxx:  use bundled version of pycxx
%global bundled_pycxx %{?_with_bundled_pycxx: 1} %{?!_with_bundled_pycxx: 0}
# rpmbuild --with=bundled_smesh:  use bundled version of Salome's Mesh
%global bundled_smesh %{?_with_bundled_smesh: 1} %{?!_with_bundled_smesh: 0}


Name:           freecad
Version:        0.13
Release:        3%{?dist}
Summary:        A general purpose 3D CAD modeler
Group:          Applications/Engineering

# This package must go in the non-free repository because of its dependence
# on OCE which is considered non-free.
License:        GPLv3+ with exception
URL:            http://sourceforge.net/apps/mediawiki/free-cad/
Source0:        http://downloads.sourceforge.net/free-cad/%{name}-%{version}.%{rev}.tar.gz
Source101:      freecad.desktop
Source102:      freecad.1

Patch0:         freecad-3rdParty.patch
Patch1:         freecad-0.13-pycxx.patch


# Utilities
%if 0%{?rhel}
BuildRequires:  cmake28
%else
BuildRequires:  cmake
%endif
BuildRequires:  doxygen swig graphviz
BuildRequires:  gcc-gfortran
BuildRequires:  gettext
BuildRequires:  dos2unix
BuildRequires:  desktop-file-utils
BuildRequires:  tbb-devel
# Development Libraries
BuildRequires:  freeimage-devel
BuildRequires:  libXmu-devel
BuildRequires:  mesa-libGLU-devel
%if %{occ}
BuildRequires:  OpenCASCADE-devel
%else
BuildRequires:  OCE-devel
%endif
# Not yet in Fedora
# https://bugzilla.redhat.com/show_bug.cgi?id=665733
#BuildRequires:  Coin3-devel
BuildRequires:  Coin2-devel
BuildRequires:  python2-devel
BuildRequires:  boost-devel
BuildRequires:  eigen3-devel
BuildRequires:  qt-devel qt-webkit-devel
BuildRequires:  SoQt-devel
# Not used yet.
#BuildRequires:  ode-devel
BuildRequires:  xerces-c xerces-c-devel
BuildRequires:  libspnav-devel
#BuildRequires:  opencv-devel
%if ! %{bundled_smesh}
BuildRequires:  smesh-devel
%endif
%if ! %{bundled_zipios}
BuildRequires:  zipios++-devel
%endif
%if ! %{bundled_pycxx}
BuildRequires:  python-pycxx-devel
%endif
BuildRequires:  libicu-devel
BuildRequires:  python-matplotlib

# Needed for plugin support and is not a soname dependency.
Requires:       python-pivy
Requires:       PyQt4
Requires:       hicolor-icon-theme
Requires:       python-matplotlib
Requires:       python-collada

# plugins and private shared libs in %%{_libdir}/freecad/lib are private;
# prevent private capabilities being advertised in Provides/Requires
%define plugin_regexp /^\\\(libFreeCAD.*%(for i in %{plugins}; do echo -n "\\\|$i\\\|$iGui"; done)\\\)\\\(\\\|Gui\\\)\\.so/d
%{?filter_setup:
%filter_provides_in %{_libdir}/%{name}/lib
%filter_from_requires %{plugin_regexp}
%filter_from_provides %{plugin_regexp}
%filter_provides_in %{_libdir}/%{name}/Mod
%filter_requires_in %{_libdir}/%{name}/Mod
%filter_setup
}


%description
FreeCAD is a general purpose Open Source 3D CAD/MCAD/CAx/CAE/PLM modeler, aimed
directly at mechanical engineering and product design but also fits a wider
range of uses in engineering, such as architecture or other engineering
specialties. It is a feature-based parametric modeler with a modular software
architecture which makes it easy to provide additional functionality without
modifying the core system.


%package doc
Summary:        Extended documentation for FreeCAD
Group:          Documentation
BuildArch:      noarch
Requires:       %{name} = %{version}-%{release}
Requires:       qt-assistant

%description doc
End user documentation for FreeCAD


%prep
#setup -q -n FreeCAD-%{version}.%{svnrev}
%setup -q -n freecad-%{version}.%{rev}
%patch0 -p1 -b .3rdparty
# Remove bundled pycxx if we're not using it
%if ! %{bundled_pycxx}
%patch1 -p1 -b .pycxx
rm -rf src/CXX
%endif

%if ! %{bundled_zipios}
rm -rf src/zipios++
%endif

# Fix encodings
dos2unix -k src/Mod/Test/unittestgui.py \
            ChangeLog.txt \
            copying.lib \
            data/License.txt

# Removed bundled libraries
rm -rf src/3rdParty


%build
rm -rf build && mkdir build && pushd build

LDFLAGS='-Wl,--as-needed'; export LDFLAGS
%cmake -DCMAKE_INSTALL_PREFIX=%{_libdir}/%{name} \
       -DCMAKE_INSTALL_DATADIR=%{_datadir}/%{name} \
       -DCMAKE_INSTALL_DOCDIR=%{_docdir}/%{name} \
       -DCMAKE_INSTALL_INCLUDEDIR=%{_includedir} \
       -DRESOURCEDIR=%{_libdir}/freecad \
       -DCOIN3D_INCLUDE_DIR=%{_includedir}/Coin2 \
       -DCOIN3D_DOC_PATH=%{_datadir}/Coin2/Coin \
       -DFREECAD_USE_EXTERNAL_PIVY=TRUE \
%if %{occ}
       -DUSE_OCC=TRUE \
%endif
%if ! %{bundled_smesh}
       -DSMESH_INCLUDE_DIR=%{_includedir} \
%endif
%if ! %{bundled_zipios}
       -DFREECAD_USE_EXTERNAL_ZIPIOS=TRUE \
%endif
%if ! %{bundled_pycxx}
       -DPYCXX_INCLUDE_DIR=$(pkg-config --variable=includedir PyCXX) \
       -DPYCXX_SOURCE_DIR=$(pkg-config --variable=srcdir PyCXX) \
%endif
       ../

make %{?_smp_mflags}

make doc


%install
pushd build
make install DESTDIR=%{buildroot}
popd

# Symlink binaries to /usr/bin
mkdir -p %{buildroot}%{_bindir}
pushd %{buildroot}%{_bindir}
ln -s ../%{_lib}/freecad/bin/FreeCAD .
ln -s ../%{_lib}/freecad/bin/FreeCADCmd .
popd

# Fix problems with unittestgui.py
#chmod +x %{buildroot}%{_libdir}/%{name}/Mod/Test/unittestgui.py

# Install desktop file
desktop-file-install                                   \
    --dir=%{buildroot}%{_datadir}/applications         \
    %{SOURCE101}
sed -i 's,@lib@,%{_lib},g' %{buildroot}%{_datadir}/applications/%{name}.desktop

# Install desktop icon
install -pD -m 0644 src/Gui/Icons/%{name}.svg \
    %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/%{name}.svg

# Install man page
install -pD -m 0644 %{SOURCE102} \
    %{buildroot}%{_mandir}/man1/%{name}.1

# Symlink manpage to other binary names
pushd %{buildroot}%{_mandir}/man1
ln -sf %{name}.1.gz FreeCAD.1.gz 
ln -sf %{name}.1.gz FreeCADCmd.1.gz
popd

# Install QT Assistant documentation
mkdir -p %{buildroot}%{_docdir}/%{name}
install -pm 0644 build/doc/freecad.* %{buildroot}%{_docdir}/%{name}/

# Bug maintainers to keep %%{plugins} macro up to date.
#
# Make sure there are no plugins that need to be added to plugins macro
new_plugins=`ls %{buildroot}%{_libdir}/freecad/lib | sed -e  '%{plugin_regexp}'`
if [ -n "$new_plugins" ]; then
    echo -e "\n\n\n**** ERROR:\n" \
        "\nPlugins not caught by regexp:  " $new_plugins \
        "\n\nPlugins in %{_libdir}/freecad/lib do not exist in" \
         "\nspecfile %%{plugins} macro.  Please add these to" \
         "\n%%{plugins} macro at top of specfile and rebuild.\n****\n" 1>&2
    exit 1
fi
# Make sure there are no entries in the plugins macro that don't match plugins
for p in %{plugins}; do
    if [ -z "`ls %{buildroot}%{_libdir}/freecad/lib/$p*.so`" ]; then
        set +x
        echo -e "\n\n\n**** ERROR:\n" \
             "\nExtra entry in %%{plugins} macro with no matching plugin:" \
             "'$p'.\n\nPlease remove from %%{plugins} macro at top of" \
             "\nspecfile and rebuild.\n****\n" 1>&2
        exit 1
    fi
done


%post
/bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :

%postun
if [ $1 -eq 0 ] ; then
    /bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null
    /usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
fi

%posttrans
/usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :


%files
%doc ChangeLog.txt copying.lib data/License.txt build/doc/*
%{_bindir}/*
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/hicolor/scalable/apps/%{name}.svg
%dir %{_libdir}/%{name}
%{_libdir}/%{name}/bin/
%{_libdir}/%{name}/lib/
%{_libdir}/%{name}/Mod/
%{_datadir}/%{name}/
%{_mandir}/man1/*.1.gz

%files doc
%{_docdir}/%{name}


%changelog
* Mon Jul 15 2013 Richard Shaw <hobbes1069@gmail.com> - 0.13-3
- Rebuild for updated OCE.

* Mon Apr 29 2013 Nicolas Chauvet <kwizart@gmail.com> - 0.13-2
- https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Mon Feb 18 2013 Richard Shaw <hobbes1069@gmail.com> - 0.13-1
- Update to latest upstream release.

* Sat Oct 20 2012 John Morris <john@zultron.com> - 0.12-9
- Use cmake28 package on el6
- Remove COIN3D_DOC_PATH cmake def (one less warning during build)
- Add PyQt as requirement.
- Add libicu-devel as build requirement.

* Wed Sep 26 2012 Richard Shaw <hobbes1069@gmail.com> - 0.12-8
- Rebuild for boost 1.50.

* Thu Jul 05 2012 Richard Shaw <hobbes1069@gmail.com> - 0.12-7
- Remove BuildRequires: tbb-devel and gts-devel
- Add missing license files to %%doc.
- Add missing requirement for hicolor-icon-theme.
- Fix excessive linking issue.
- Other minor spec updates.

* Mon Jun 25 2012  <john@zultron.com> - 0.12-6
- Filter out automatically generated Provides/Requires of private libraries
- freecad.desktop not passing 'desktop-file-validate'; fixed
- Remove BuildRequires: tbb-devel and gts-devel
- Update license tag to GPLv3+ only.
- Add missing license files to %%doc.
- Add missing build requirement for hicolor-icon-theme.
- Fix excessive linking issue.
- Other minor spec updates.

* Mon Jun 25 2012  <john@zultron.com> - 0.12-5
- New patch to unbundle PyCXX
- Add conditional build options for OpenCASCADE, bundled Zipios++,
  bundled PyCXX, bundled smesh

* Tue Jun 19 2012 Richard Shaw <hobbes1069@gmail.com> - 0.12-4
- Add linker flag to stop excessive linking.

* Thu May 31 2012 Richard Shaw <hobbes1069@gmail.com> - 0.12-3
- Add patch for GCC 4.7 on Fedora 17.

* Thu Nov 10 2011 Richard Shaw <hobbes1069@gmail.com> - 0.12-2
- Initial release.
