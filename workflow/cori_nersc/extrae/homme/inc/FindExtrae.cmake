
IF (DEFINED EXTRAE_LIB) 
  #find_library(Extrae_LIBRARY 
  #             NAMES ${EXTRAE_LIB}
  #             HINTS ${EXTRAE_DIR} 
  #             PATH_SUFFIXES lib lib64
  #             NO_SYSTEM_ENVIRONMENT_PATH NO_CMAKE_SYSTEM_PATH)
  #SET(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -L${EXTRAE_DIR}/lib -l${EXTRAE_LIB}")
  SET(ExtraeS_LIBRARY "-L${EXTRAE_DIR}/lib -l${EXTRAE_LIB} -L/opt/cray/pe/papi/5.5.1.1/lib -lpapi -L/usr/common/software/libxml2/2.9.3/hsw/lib -lxml2 -L/usr/common/software/libunwind/1.1/hsw/lib -lunwind /global/homes/g/grnydawn/opt/binutils/2.27/lib64/libiberty.a /global/homes/g/grnydawn/opt/binutils/2.27/lib/libbfd.a")
  #SET(ExtraeS_LIBRARY "-L${EXTRAE_DIR}/lib -l${EXTRAE_LIB} -L/opt/cray/pe/papi/5.5.1.1/lib -lpapi -L/global/homes/g/grnydawn/opt/zlib/1.2.11/lib -lz -L/global/homes/g/grnydawn/opt/xml2/2.9.4/lib -lxml2 -L/global/homes/g/grnydawn/opt/libunwind/1.2/lib -lunwind /global/homes/g/grnydawn/opt/binutils/2.27/lib/libbfd.a /global/homes/g/grnydawn/opt/binutils/2.27/lib64/libiberty.a")
  #SET(ExtraeS_LIBRARY "-L${EXTRAE_DIR}/lib -l${EXTRAE_LIB}")

ELSE ()

  #find_library(Extrae_LIBRARY 
  #             NAMES mpitracef
  #             HINTS ${EXTRAE_DIR} 
  #             PATH_SUFFIXES lib lib64
  #             NO_SYSTEM_ENVIRONMENT_PATH NO_CMAKE_SYSTEM_PATH)
  #SET(ExtraeS_LIBRARY "-L${EXTRAE_DIR}/lib -lmpitracef")
  SET(ExtraeS_LIBRARY "-L${EXTRAE_DIR}/lib -lmpitracef -L/opt/cray/pe/papi/5.5.1.1/lib -lpapi -L/usr/common/software/libxml2/2.9.3/hsw/lib -lxml2 -L/usr/common/software/libunwind/1.1/hsw/lib -lunwind /global/homes/g/grnydawn/opt/binutils/2.27/lib64/libiberty.a /global/homes/g/grnydawn/opt/binutils/2.27/lib/libbfd.a")
  #SET(ExtraeS_LIBRARY "-L${EXTRAE_DIR}/lib -lmpitracef -L/opt/cray/pe/papi/5.5.1.1/lib -lpapi -L/global/homes/g/grnydawn/opt/zlib/1.2.11/lib -lz -L/global/homes/g/grnydawn/opt/xml2/2.9.4/lib -lxml2 -L/global/homes/g/grnydawn/opt/libunwind/1.2/lib -lunwind /global/homes/g/grnydawn/opt/binutils/2.27/lib/libbfd.a /global/homes/g/grnydawn/opt/binutils/2.27/lib64/libiberty.a")
  #SET(ExtraeS_LIBRARY "-L${EXTRAE_DIR}/lib -lmpitracef -L/opt/cray/pe/papi/5.5.1.1/lib -lpapi -L/usr/common/software/libxml2/2.9.3/hsw/lib -lxml2 -L/usr/common/software/libunwind/1.1/hsw/lib -lunwind /usr/lib64/libbfd.a /usr/lib64/libiberty.a")
  #SET(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -L${EXTRAE_DIR}/lib -lmpitracef")

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
