# M4-Based Header-Only Atom Type System

## Overview

This directory now uses an m4-based, header-only implementation for atom type generation, replacing the previous CMake-based system that required separate .cc source files.

## Benefits

1. **Pure m4 Processing**: All type definitions are processed using the GNU m4 macro processor
2. **Header-Only**: No separate .cc files needed for type definitions (atom_types_init.cc is no longer required)
3. **Simplified Build**: Fewer compilation units, faster builds
4. **Better Maintainability**: The m4 macros are easier to understand and modify than CMake scripts

## Files

### Core Files

- **atom_types.script**: The source file defining all atom types (unchanged format)
- **atom_types.m4**: M4 macro definitions for generating C++ headers
- **generate_types.py**: Python script that converts atom_types.script to m4 input files

### Generated Files (by Python script)

- **atom_types.h.m4**: M4 input for generating atom_types.h
- **atom_types_init.h.m4**: M4 input for generating atom_types_init.h
- **atom_names.h.m4**: M4 input for generating atom_names.h

### Final Generated Files (by m4)

- **atom_types.h**: Header-only type declarations
- **atom_types_init.h**: Header-only type registration (replaces atom_types_init.cc)
- **atom_names.h**: Inline constructor helpers

## Build Process

The build process now follows these steps:

1. **Script Processing**: `generate_types.py` reads `atom_types.script` and generates `.m4` files
2. **M4 Processing**: The m4 macro processor transforms `.m4` files into final `.h` headers
3. **Compilation**: Only `NameServer.cc` needs to be compiled (header-only for types)

```
atom_types.script
    ↓ (generate_types.py)
atom_types.h.m4, atom_types_init.h.m4, atom_names.h.m4
    ↓ (m4)
atom_types.h, atom_types_init.h, atom_names.h (header-only)
```

## Usage

### For Developers

The atom type system is now completely header-only. Just include the appropriate headers:

```cpp
#include <opencog/atoms/atom_types/atom_types.h>
#include <opencog/atoms/atom_types/atom_types_init.h>
#include <opencog/atoms/atom_types/atom_names.h>

// Type initialization happens automatically via static initialization
// No need to call init functions explicitly
```

### For Build System Maintainers

The CMakeLists.txt uses these custom commands:

1. Generate m4 input: `python3 generate_types.py atom_types.script`
2. Process with m4: `m4 -I<source_dir> <file>.m4 > <file>.h`

Requirements:
- GNU m4 (usually pre-installed on Unix systems)
- Python 3 (for the conversion script)

## Comparison with Old System

### Old System (CMake-based)

- Used CMake macros to generate C++ code
- Required separate .cc files for type initialization
- Generated: atom_types.h, atom_types.definitions, atom_types.inheritance
- Initialization via atom_types_init.cc

### New System (M4-based)

- Uses m4 macros to generate C++ code
- **Header-only** - no .cc files for type initialization
- Generated: atom_types.h, atom_types_init.h, atom_names.h
- Initialization via static constructors in headers

## Technical Details

### Header-Only Type Storage

Instead of extern declarations + separate definitions:

```cpp
// Old way
extern Type MY_TYPE;  // in .h
Type MY_TYPE;         // in .cc
```

We now use inline functions with static locals:

```cpp
// New way (header-only)
inline Type& get_MY_TYPE() {
    static Type type_instance = 0;
    return type_instance;
}
#define MY_TYPE get_MY_TYPE()
```

### Static Initialization

Type registration happens automatically via a static initializer:

```cpp
static struct AtomTypesInitializer {
    AtomTypesInitializer() { init_atom_types(); }
} _atom_types_initializer;
```

This ensures types are registered before main() runs, without requiring explicit init calls.

## Maintenance

### Adding New Atom Types

Just edit `atom_types.script` as before. The build system will automatically:
1. Regenerate the .m4 files
2. Process them with m4
3. Generate updated header files

### Modifying the Generation System

- **To change header generation**: Edit `atom_types.m4` (m4 macros)
- **To change script processing**: Edit `generate_types.py`
- **To change build integration**: Edit `CMakeLists.txt`

## Migration Notes

The atom_types_init.cc file is no longer needed and has been removed from the build. The NameServer.cc is still compiled as it contains the NameServer class implementation.

Code that previously included atom_types.definitions or atom_types.inheritance should now include atom_types_init.h.
