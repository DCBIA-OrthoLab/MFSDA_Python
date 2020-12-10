cmake_minimum_required(VERSION 3.13.4)

project(MFSDA)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://github.com/DCBIA-OrthoLab/MFSDA_Python#readme")
set(EXTENSION_CATEGORY "Shape Analysis")
set(EXTENSION_CONTRIBUTORS "Mateo Lopez (University of North Carolina), Juan Carlos Prieto (University of North Carolina) ")
set(EXTENSION_DESCRIPTION "Modules for statistical shape analysis. A multivariate varying coefficient model is introduced to build the association between the multivariate shape measurements and demographic information and other clinical variables. Statistical inference, i.e., hypothesis testing, is also included in this package, which can be used in investigating whether some covariates of interest are significantly associated with the shape information. The hypothesis testing results are further used in clustering based analysis.")
set(EXTENSION_ICONURL "https://raw.githubusercontent.com/DCBIA-OrthoLab/MFSDA_Python/master/MFSDA.png")
set(EXTENSION_SCREENSHOTURLS "https://raw.githubusercontent.com/DCBIA-OrthoLab/MFSDA_Python/master/MFSDA/Resources/Icons/RunMFSDA.png https://raw.githubusercontent.com/DCBIA-OrthoLab/MFSDA_Python/master/MFSDA/Resources/Icons/SelectVariables.png")
set(EXTENSION_DEPENDS "NA") # Specified as a list or "NA" if no dependencies)
set(EXTENSION_BUILD_SUBDIRECTORY inner-build)

set(SUPERBUILD_TOPLEVEL_PROJECT inner)

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})
mark_as_superbuild(Slicer_DIR)

find_package(Git REQUIRED)
mark_as_superbuild(GIT_EXECUTABLE)

#-----------------------------------------------------------------------------
# SuperBuild setup
option(${EXTENSION_NAME}_SUPERBUILD "Build ${EXTENSION_NAME} and the projects it depends on." ON)
mark_as_advanced(${EXTENSION_NAME}_SUPERBUILD)
if(${EXTENSION_NAME}_SUPERBUILD)
  include("${CMAKE_CURRENT_SOURCE_DIR}/SuperBuild.cmake")
  return()
endif()

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(MFSDA)
## NEXT_MODULE

if(NOT Slicer_SOURCE_DIR)
  #-----------------------------------------------------------------------------
  # Install extension python packages
  install(CODE "message(\"CPack: - Install directory: ${python_packages_DIR}\")")
  install(
      DIRECTORY "${python_packages_DIR}/"
      DESTINATION ${Slicer_INSTALL_ROOT}${Slicer_BUNDLE_EXTENSIONS_LOCATION}
      COMPONENT RuntimeLibraries
      )
endif()

#-----------------------------------------------------------------------------
set(EXTENSION_CPACK_INSTALL_CMAKE_PROJECTS)
set(${EXTENSION_NAME}_CPACK_INSTALL_CMAKE_PROJECTS "${EXTENSION_CPACK_INSTALL_CMAKE_PROJECTS}" CACHE STRING "List of external projects to install" FORCE)

#-----------------------------------------------------------------------------
list(APPEND CPACK_INSTALL_CMAKE_PROJECTS "${CMAKE_BINARY_DIR};${EXTENSION_NAME};ALL;/")
list(APPEND CPACK_INSTALL_CMAKE_PROJECTS "${${EXTENSION_NAME}_CPACK_INSTALL_CMAKE_PROJECTS}")
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})

