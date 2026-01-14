#!/usr/bin/env python3
"""
Generate atom type files from atom_types.script using m4 macros.
This script processes the atom_types.script file and generates m4-processable files
for a header-only implementation.
"""

import re
import sys
from typing import List, Tuple, Optional

def camel_case(name: str) -> str:
    """Convert UPPER_CASE to CamelCase"""
    parts = name.split('_')
    return ''.join(word.capitalize() for word in parts)

def strip_suffix(name: str, suffix: str) -> str:
    """Strip suffix from name if present"""
    if name.endswith(suffix):
        return name[:-len(suffix)]
    return name

def parse_type_line(line: str) -> Optional[Tuple[str, List[str], Optional[str]]]:
    """
    Parse a type definition line.
    Returns (TYPE, [PARENT_TYPES], TYPE_NAME) or None if not a type definition.
    """
    # Remove comments
    line = re.sub(r'//.*$', '', line).strip()
    if not line:
        return None
    
    # Match patterns like:
    # TYPE
    # TYPE <- PARENT
    # TYPE <- PARENT1,PARENT2
    # TYPE <- PARENT "CustomName"
    # TYPE "CustomName"
    
    # Full pattern with optional parents and custom name
    match = re.match(r'^([A-Z_][A-Z0-9_]*)\s*(?:<-\s*([A-Z_][A-Z0-9_,\s]*))?\s*(?:"([^"]+)")?', line)
    if not match:
        return None
    
    type_name = match.group(1)
    parent_str = match.group(2)
    custom_name = match.group(3)
    
    parents = []
    if parent_str:
        parents = [p.strip() for p in parent_str.split(',')]
    
    return (type_name, parents, custom_name)

def generate_header(types_data: List[Tuple[str, List[str], Optional[str]]]) -> str:
    """Generate the atom_types.h header file (m4 input)"""
    output = []
    output.append('include(`atom_types.m4\')dnl')
    output.append('ATOM_TYPES_HEADER_INIT')
    output.append('')
    
    for type_name, parents, custom_name in types_data:
        output.append(f'DEFINE_TYPE_INLINE([{type_name}])')
    
    output.append('')
    output.append('ATOM_TYPES_HEADER_END')
    return '\n'.join(output)

def generate_init(types_data: List[Tuple[str, List[str], Optional[str]]]) -> str:
    """Generate the atom_types_init.h initialization header (m4 input)"""
    output = []
    output.append('include(`atom_types.m4\')dnl')
    output.append('TYPE_REGISTRATION_INIT')
    output.append('')
    
    for type_name, parents, custom_name in types_data:
        type_str = camel_case(type_name) if not custom_name else custom_name
        short_name = strip_suffix(type_str, 'Link')
        short_name = strip_suffix(short_name, 'Node')
        if short_name == type_str or not short_name:
            short_name = type_str
        
        parent_str = parents[0] if parents else ''
        output.append(f'REGISTER_TYPE_INLINE([{type_name}], [{parent_str}], [{type_str}], [{short_name}])')
    
    output.append('')
    output.append('TYPE_REGISTRATION_END')
    return '\n'.join(output)

def generate_atom_names(types_data: List[Tuple[str, List[str], Optional[str]]]) -> str:
    """Generate the atom_names.h file (m4 input)"""
    output = []
    output.append('include(`atom_types.m4\')dnl')
    output.append('ATOM_NAMES_INIT')
    output.append('')
    
    for type_name, parents, custom_name in types_data:
        type_str = camel_case(type_name) if not custom_name else custom_name
        
        # Check if it's a Link type
        if 'LINK' in type_name or type_str.endswith('Link'):
            short_name = strip_suffix(type_str, 'Link')
            if short_name and short_name != type_str and short_name not in ['Atom', 'Frame', 'Type', 'Notype']:
                output.append(f'LINK_CTOR_INLINE([{short_name}], [{type_name}])')
        
        # Check if it's a Node type
        if 'NODE' in type_name or type_str.endswith('Node'):
            short_name = strip_suffix(type_str, 'Node')
            if short_name and short_name != type_str and short_name != 'Type':
                output.append(f'NODE_CTOR_INLINE([{short_name}], [{type_name}])')
    
    output.append('')
    output.append('ATOM_NAMES_END')
    return '\n'.join(output)

def main():
    if len(sys.argv) < 2:
        print("Usage: generate_types.py <atom_types.script>")
        sys.exit(1)
    
    script_file = sys.argv[1]
    
    # Parse the script file
    types_data = []
    with open(script_file, 'r') as f:
        for line in f:
            result = parse_type_line(line)
            if result:
                types_data.append(result)
    
    # Generate output files (as m4 input)
    with open('atom_types.h.m4', 'w') as f:
        f.write(generate_header(types_data))
    
    with open('atom_types_init.h.m4', 'w') as f:
        f.write(generate_init(types_data))
    
    with open('atom_names.h.m4', 'w') as f:
        f.write(generate_atom_names(types_data))
    
    print(f"Generated m4 input for {len(types_data)} type definitions")
    print("Run m4 on the .m4 files to generate final headers:")
    print("  m4 atom_types.h.m4 > atom_types.h")
    print("  m4 atom_types_init.h.m4 > atom_types_init.h")
    print("  m4 atom_names.h.m4 > atom_names.h")

if __name__ == '__main__':
    main()
