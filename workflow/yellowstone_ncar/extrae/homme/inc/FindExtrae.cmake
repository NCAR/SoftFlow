
IF (DEFINED EXTRAE_LIB) 
  #find_library(Extrae_LIBRARY 
  #             NAMES ${EXTRAE_LIB}
  #             HINTS ${EXTRAE_DIR} 
  #             PATH_SUFFIXES lib lib64
  #             NO_SYSTEM_ENVIRONMENT_PATH NO_CMAKE_SYSTEM_PATH)
  #SET(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -L${EXTRAE_DIR}/lib -l${EXTRAE_LIB}")
  #SET(XML2_LIBRARY "/usr/common/software/libxml2/2.9.3/hsw/lib/libxml2.a")
  #SET(BFD_LIBRARY "/usr/lib64/libbfd.a")
  SET(ExtraeS_LIBRARY "-L${EXTRAE_DIR}/lib -l${EXTRAE_LIB} -L/glade/apps/opt/papi/5.4.3/intel/15.0.3/lib -lpapi -L/glade/apps/opt/libxml2/2.9.0/gnu/4.7.2/lib -lxml2 -L/glade/p/tdd/asap/contrib/libunwind/1.1/gnu/lib -lunwind /usr/lib64/libbfd.a /usr/lib64/libiberty.a")
  #SET(ExtraeS_LIBRARY "-L${EXTRAE_DIR}/lib -l${EXTRAE_LIB}")


ELSE ()

  #find_library(Extrae_LIBRARY 
  #             NAMES mpitracef
  #             HINTS ${EXTRAE_DIR} 
  #             PATH_SUFFIXES lib lib64
  #             NO_SYSTEM_ENVIRONMENT_PATH NO_CMAKE_SYSTEM_PATH)
  #SET(ExtraeS_LIBRARY "-L${EXTRAE_DIR}/lib -lmpitracef")
  SET(ExtraeS_LIBRARY "-L${EXTRAE_DIR}/lib -lmpitracef -L/glade/apps/opt/papi/5.4.3/intel/15.0.3/lib -lpapi -L/glade/apps/opt/libxml2/2.9.0/gnu/4.7.2/lib -lxml2 -L/glade/p/tdd/asap/contrib/libunwind/1.1/gnu/lib -lunwind /usr/lib64/libbfd.a /usr/lib64/libiberty.a")
  #SET(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -L${EXTRAE_DIR}/lib -lmpitracef")
  #SET(XML2_LIBRARY "/usr/common/software/libxml2/2.9.3/hsw/lib/libxml2.a")
  #SET(BFD_LIBRARY "/usr/lib64/libbfd.a")

ENDIF ()

IF (ExtraeS_LIBRARY) 
  SET(Extrae_FOUND TRUE)
ELSE ()
  SET(Extrae_FOUND FALSE)
ENDIF ()


IF(Extrae_FIND_REQUIRED AND NOT Extrae_FOUND)
  MESSAGE(FATAL_ERROR "Did not find required library Extrae")
ELSE ()
  MESSAGE(STATUS "Found Extrae:")
  MESSAGE(STATUS "  Libraries: ${ExtraeS_LIBRARY}")
ENDIF()
