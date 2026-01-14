
# M4-based atom type generation (header-only implementation)
# This replaces the previous CMake-based generation

# Find m4 processor
FIND_PROGRAM(M4_EXECUTABLE m4)
IF(NOT M4_EXECUTABLE)
	MESSAGE(FATAL_ERROR "m4 macro processor not found. Please install m4.")
ENDIF()

# Generate m4 input files from atom_types.script
ADD_CUSTOM_COMMAND(
	OUTPUT 
		${CMAKE_CURRENT_BINARY_DIR}/atom_types.h.m4
		${CMAKE_CURRENT_BINARY_DIR}/atom_types_init.h.m4
		${CMAKE_CURRENT_BINARY_DIR}/atom_names.h.m4
	COMMAND ${CMAKE_COMMAND} -E env 
		python3 ${CMAKE_CURRENT_SOURCE_DIR}/generate_types.py 
		${CMAKE_CURRENT_SOURCE_DIR}/atom_types.script
	WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
	DEPENDS 
		${CMAKE_CURRENT_SOURCE_DIR}/atom_types.script
		${CMAKE_CURRENT_SOURCE_DIR}/generate_types.py
	COMMENT "Generating m4 input files from atom_types.script"
)

# Process m4 files to generate final headers
ADD_CUSTOM_COMMAND(
	OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/atom_types.h
	COMMAND ${M4_EXECUTABLE} 
		-I${CMAKE_CURRENT_SOURCE_DIR}
		${CMAKE_CURRENT_BINARY_DIR}/atom_types.h.m4
		> ${CMAKE_CURRENT_BINARY_DIR}/atom_types.h
	DEPENDS 
		${CMAKE_CURRENT_BINARY_DIR}/atom_types.h.m4
		${CMAKE_CURRENT_SOURCE_DIR}/atom_types.m4
	COMMENT "Processing atom_types.h.m4 with m4"
)

ADD_CUSTOM_COMMAND(
	OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/atom_types_init.h
	COMMAND ${M4_EXECUTABLE}
		-I${CMAKE_CURRENT_SOURCE_DIR}
		${CMAKE_CURRENT_BINARY_DIR}/atom_types_init.h.m4
		> ${CMAKE_CURRENT_BINARY_DIR}/atom_types_init.h
	DEPENDS 
		${CMAKE_CURRENT_BINARY_DIR}/atom_types_init.h.m4
		${CMAKE_CURRENT_SOURCE_DIR}/atom_types.m4
	COMMENT "Processing atom_types_init.h.m4 with m4"
)

ADD_CUSTOM_COMMAND(
	OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/atom_names.h
	COMMAND ${M4_EXECUTABLE}
		-I${CMAKE_CURRENT_SOURCE_DIR}
		${CMAKE_CURRENT_BINARY_DIR}/atom_names.h.m4
		> ${CMAKE_CURRENT_BINARY_DIR}/atom_names.h
	DEPENDS 
		${CMAKE_CURRENT_BINARY_DIR}/atom_names.h.m4
		${CMAKE_CURRENT_SOURCE_DIR}/atom_types.m4
	COMMENT "Processing atom_names.h.m4 with m4"
)

# Still generate scheme and python bindings using the old system for now
OPENCOG_GEN_SCM_ATOMTYPES(atom_types.script core_types.scm)
OPENCOG_GEN_PYTHON_ATOMTYPES(atom_types.script core_types.pyx)

# This is done in the OCaml directory.
# OPENCOG_GEN_OCAML_ATOMTYPES(atom_types.script atoms.ml mlwrappers.cc)

# The target `opencog_atom_types` is satisfied when `atom_types.h`
# appears in the file system. This target is used in other
# CMakefiles to make sure that this directory is visited, first.
ADD_CUSTOM_TARGET(opencog_atom_types
	DEPENDS 
		atom_types.h 
		atom_types_init.h
		atom_names.h
		core_types.scm 
		core_types.pyx)

# The atom_types.h file is written to the build directory
INCLUDE_DIRECTORIES(${CMAKE_BINARY_DIR})

# ADD_DEFINITIONS(-DLOAD_ME_FIRST)
ADD_COMPILE_DEFINITIONS(LOAD_ME_FIRST)

# Header-only library - only needs NameServer.cc now
# atom_types_init.cc is no longer needed (header-only)
ADD_LIBRARY (atom_types
	NameServer.cc
	)

# Without this, parallel make will race and crap up the generated files.
# Actually, that's not true ... even with this, compilation of other
# units might start before the generation has finished.  Ugh.
ADD_DEPENDENCIES(atom_types opencog_atom_types)

TARGET_LINK_LIBRARIES(atom_types
	${COGUTIL_LIBRARY}
	)

INSTALL (TARGETS atom_types EXPORT AtomSpaceTargets
	DESTINATION "${CMAKE_INSTALL_LIBDIR}/opencog"
	)

INSTALL (FILES
	${CMAKE_CURRENT_BINARY_DIR}/atom_types.h
	${CMAKE_CURRENT_BINARY_DIR}/atom_types_init.h
	${CMAKE_CURRENT_BINARY_DIR}/atom_names.h
	NameServer.h
	types.h
	DESTINATION "include/opencog/atoms/atom_types"
	)

# Install the auto-generated atom types as well
ADD_GUILE_MODULE (FILES
	${CMAKE_CURRENT_BINARY_DIR}/core_types.scm
	MODULE "opencog"
	MODULE_DESTINATION "${GUILE_SITE_DIR}/opencog/base"
	DEPENDS opencog_atom_types
	)
