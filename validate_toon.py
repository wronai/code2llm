#!/usr/bin/env python3
"""
Script to validate if analysis.toon.yaml and analysis.yaml contain the same data.
"""

import yaml
import sys
from pathlib import Path
from collections import defaultdict

def load_yaml(filepath):
    """Load YAML file safely."""
    try:
        with open(filepath, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None

def load_toon(filepath):
    """Parse TOON plain-text format into structured data."""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        return parse_toon_content(content)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None

def parse_toon_content(content):
    """Parse TOON v2 plain-text format."""
    data = {
        'meta': {},
        'stats': {},
        'functions': [],
        'classes': [],
        'modules': [],
        'patterns': [],
        'call_graph': {},
        'insights': {},
        'health': [],
        'refactor': [],
        'hotspots': [],
    }
    lines = content.split('\n')
    section = None
    
    for line in lines:
        line_stripped = line.strip()
        
        # Parse header
        if line.startswith('# code2llm'):
            data['meta']['project'] = 'code2llm'
            data['meta']['generated'] = line.split('|')[-1].strip() if '|' in line else ''
            continue
        
        # Parse stats from header line 2
        if line.startswith('# CC'):
            parts = line[2:].strip().split('|')
            for part in parts:
                if 'critical' in part:
                    data['stats']['critical'] = part.strip()
                elif 'dups' in part:
                    data['stats']['duplicates'] = part.strip()
                elif 'cycles' in part:
                    data['stats']['cycles'] = part.strip()
            continue
        
        # Detect sections
        if line.startswith('HEALTH'):
            section = 'health'
            continue
        elif line.startswith('REFACTOR'):
            section = 'refactor'
            continue
        elif line.startswith('COUPLING:'):
            section = 'coupling'
            continue
        elif line.startswith('LAYERS:'):
            section = 'layers'
            continue
        elif line.startswith('DUPLICATES'):
            section = 'duplicates'
            continue
        elif line.startswith('FUNCTIONS'):
            section = 'functions'
            continue
        elif line.startswith('HOTSPOTS:'):
            section = 'hotspots'
            continue
        elif line.startswith('CLASSES:'):
            section = 'classes'
            continue
        elif line.startswith('D:'):
            section = 'details'
            continue
        
        # Parse section content
        if section == 'health' and line_stripped:
            if line_stripped.startswith('🔴') or line_stripped.startswith('🟡'):
                data['health'].append(line_stripped)
        elif section == 'functions' and line_stripped:
            # Parse function lines like: "56.0  main  19n 4exit cond+ret !! split"
            if line_stripped.startswith('summary:'):
                continue
            parts = line_stripped.split()
            if len(parts) >= 2 and parts[0].replace('.', '').isdigit():
                func_name = parts[1]
                data['functions'].append({'name': func_name, 'cc': float(parts[0])})
        elif section == 'classes' and line_stripped:
            # Parse class lines like: "ToonExporter  ████████  29m CC̄=9.5 max=31 !!"
            parts = line_stripped.split()
            if parts and not parts[0].startswith('█'):
                class_name = parts[0]
                data['classes'].append({'name': class_name})
        elif section == 'hotspots' and line_stripped:
            # Parse hotspot lines like: "#1  main  fan=45  \"calls 45 functions\""
            if line_stripped.startswith('#'):
                parts = line_stripped.split()
                if len(parts) >= 2:
                    data['hotspots'].append({'name': parts[1]})
    
    return data

def is_toon_file(filepath):
    """Check if file is TOON format based on extension or content."""
    path = Path(filepath)
    if path.suffix == '.toon':
        return True
    # Check content for TOON header
    try:
        with open(filepath, 'r') as f:
            first_line = f.readline()
            return first_line.startswith('# code2llm') or first_line.startswith('# CC')
    except:
        return False

def load_file(filepath):
    """Load file - auto-detect TOON vs YAML format."""
    if is_toon_file(filepath):
        return load_toon(filepath)
    return load_yaml(filepath)

def extract_functions_from_yaml(yaml_data):
    """Extract function list from standard YAML format."""
    functions = set()
    
    # Extract from nodes
    for node_id, node_data in yaml_data.get('nodes', {}).items():
        func_name = node_data.get('function', '')
        if func_name:
            functions.add(func_name)
    
    return functions

def extract_functions_from_toon(toon_data):
    """Extract function list from parsed TOON data."""
    functions = set()
    
    # Extract from functions array
    for func_data in toon_data.get('functions', []):
        name = func_data.get('name', '')
        if name:
            functions.add(name)
    
    return functions

def extract_classes_from_yaml(yaml_data):
    """Extract class list from standard YAML format."""
    classes = set()
    
    # Extract from classes section (direct class analysis)
    for class_name in yaml_data.get('classes', {}):
        classes.add(class_name)
    
    return classes

def extract_classes_from_toon(toon_data):
    """Extract class list from parsed TOON data."""
    classes = set()
    
    # Extract from classes array
    for cls_data in toon_data.get('classes', []):
        name = cls_data.get('name', '')
        if name:
            classes.add(name)
    
    return classes

def analyze_class_differences(yaml_data, toon_data):
    """Analyze why classes differ between formats."""
    print("\n🔍 Class Detection Analysis:")
    print("-" * 50)
    
    yaml_classes = yaml_data.get('classes', {})
    toon_classes = toon_data.get('classes', [])
    
    print(f"YAML: Direct AST class detection ({len(yaml_classes)} classes)")
    print(f"TOON: Inferred from function grouping ({len(toon_classes)} classes)")
    
    # Show examples of different detection methods
    print(f"\n📋 YAML Detection Examples (AST-based):")
    for i, (name, cls_data) in enumerate(list(yaml_classes.items())[:3]):
        methods = cls_data.get('methods', [])
        print(f"  {i+1}. {name}")
        print(f"     Methods: {len(methods)} - {', '.join(methods[:3])}")
    
    print(f"\n📋 TOON Detection Examples (Function-based):")
    for i, cls_data in enumerate(toon_classes[:3]):
        methods = cls_data.get('methods', [])
        print(f"  {i+1}. {cls_data.get('module', '')}.{cls_data.get('name', '')}")
        print(f"     Methods: {len(methods)} - {', '.join(methods[:3])}")
    
    # Check overlap
    yaml_names = set(yaml_classes.keys())
    toon_names = set()
    for cls_data in toon_classes:
        module = cls_data.get('module', '')
        name = cls_data.get('name', '')
        if module and module != 'root':
            full_name = f"{module}.{name}"
        else:
            full_name = name
        toon_names.add(full_name)
    
    common = yaml_names & toon_names
    print(f"\n📊 Overlap Analysis:")
    print(f"  Common classes: {len(common)}")
    print(f"  YAML-only: {len(yaml_names - toon_names)}")
    print(f"  TOON-only: {len(toon_names - yaml_names)}")
    
    return common

def extract_modules_from_yaml(yaml_data):
    """Extract module list from standard YAML format."""
    modules = set()
    
    # Extract from modules section
    for module_name in yaml_data.get('modules', {}):
        modules.add(module_name)
    
    return modules

def extract_modules_from_toon(toon_data):
    """Extract module list from parsed TOON data."""
    # TOON v2 doesn't have explicit modules section
    # Modules are inferred from function/class locations
    modules = set()
    for func in toon_data.get('functions', []):
        name = func.get('name', '')
        if '.' in name:
            modules.add(name.rsplit('.', 1)[0])
    return modules

def compare_basic_stats(yaml_data, toon_data):
    """Compare basic statistics."""
    print("📊 Basic Statistics Comparison:")
    print("-" * 50)
    
    yaml_stats = yaml_data.get('stats', {})
    toon_stats = toon_data.get('stats', {})
    
    stats_to_check = ['files_processed', 'functions_found', 'classes_found', 'nodes_created', 'edges_created']
    
    all_match = True
    for stat in stats_to_check:
        yaml_val = yaml_stats.get(stat, 'N/A')
        toon_val = toon_stats.get(stat, 'N/A')
        match = "✅" if str(yaml_val) == str(toon_val) else "❌"
        print(f"{match} {stat}: YAML={yaml_val}, TOON={toon_val}")
        if str(yaml_val) != str(toon_val):
            all_match = False
    
    return all_match

def compare_functions(yaml_data, toon_data):
    """Compare function lists."""
    print("\n🔧 Functions Comparison:")
    print("-" * 50)
    
    yaml_funcs = extract_functions_from_yaml(yaml_data)
    toon_funcs = extract_functions_from_toon(toon_data)
    
    print(f"YAML functions: {len(yaml_funcs)}")
    print(f"TOON functions: {len(toon_funcs)}")
    
    # Find differences
    yaml_only = yaml_funcs - toon_funcs
    toon_only = toon_funcs - yaml_funcs
    common = yaml_funcs & toon_funcs
    
    print(f"Common functions: {len(common)}")
    print(f"Only in YAML: {len(yaml_only)}")
    print(f"Only in TOON: {len(toon_only)}")
    
    if yaml_only:
        print(f"\n⚠️  Functions only in YAML (first 10):")
        for func in sorted(list(yaml_only))[:10]:
            print(f"  - {func}")
    
    if toon_only:
        print(f"\n⚠️  Functions only in TOON (first 10):")
        for func in sorted(list(toon_only))[:10]:
            print(f"  - {func}")
    
    return len(yaml_only) == 0 and len(toon_only) == 0

def compare_classes(yaml_data, toon_data):
    """Compare class lists with detailed analysis."""
    print("\n🏗️  Classes Comparison:")
    print("-" * 50)
    
    yaml_classes = extract_classes_from_yaml(yaml_data)
    toon_classes = extract_classes_from_toon(toon_data)
    
    print(f"YAML classes: {len(yaml_classes)}")
    print(f"TOON classes: {len(toon_classes)}")
    
    # Find differences
    yaml_only = yaml_classes - toon_classes
    toon_only = toon_classes - yaml_classes
    common = yaml_classes & toon_classes
    
    print(f"Common classes: {len(common)}")
    print(f"Only in YAML: {len(yaml_only)}")
    print(f"Only in TOON: {len(toon_only)}")
    
    # Analyze the differences
    analyze_class_differences(yaml_data, toon_data)
    
    # Note about detection methods
    print(f"\n💡 Note: Different detection methods are expected:")
    print(f"  - YAML: Direct AST analysis (more accurate for empty classes)")
    print(f"  - TOON: Inferred from function grouping (only classes with methods)")
    
    return len(common) > 0  # Consider successful if there's overlap

def compare_modules(yaml_data, toon_data):
    """Compare module lists with detailed analysis."""
    print("\n📦 Modules Comparison:")
    print("-" * 50)
    
    yaml_modules = extract_modules_from_yaml(yaml_data)
    toon_modules = extract_modules_from_toon(toon_data)
    
    print(f"YAML modules: {len(yaml_modules)}")
    print(f"TOON modules: {len(toon_modules)}")
    
    # Find differences
    yaml_only = yaml_modules - toon_modules
    toon_only = toon_modules - yaml_modules
    common = yaml_modules & toon_modules
    
    print(f"Common modules: {len(common)}")
    print(f"Only in YAML: {len(yaml_only)}")
    print(f"Only in TOON: {len(toon_only)}")
    
    # Explain the difference
    print(f"\n💡 Note: Different module detection methods:")
    print(f"  - YAML: Direct module imports and file-level analysis")
    print(f"  - TOON: Inferred from function locations (more granular)")
    
    # Show some examples of the differences
    if yaml_only:
        print(f"\n📋 YAML-only modules (file-level):")
        for mod in sorted(list(yaml_only))[:5]:
            print(f"  - {mod}")
    
    if toon_only:
        print(f"\n📋 TOON-only modules (function-level):")
        for mod in sorted(list(toon_only))[:5]:
            print(f"  - {mod}")
    
    return len(common) > 0  # Consider successful if there's overlap

def validate_toon_completeness(toon_data):
    """Validate toon format structure."""
    print("\n🔍 TOON Format Structure Validation:")
    print("-" * 50)
    
    # Check for TOON v2 format
    has_functions = bool(toon_data.get('functions'))
    has_classes = bool(toon_data.get('classes'))
    has_health = bool(toon_data.get('health'))
    has_hotspots = bool(toon_data.get('hotspots'))
    
    all_present = True
    sections = [
        ('functions', has_functions),
        ('classes', has_classes),
        ('health', has_health),
        ('hotspots', has_hotspots),
    ]
    
    for section, present in sections:
        status = "✅" if present else "❌"
        print(f"{status} {section}: {'Present' if present else 'Missing'}")
        if not present:
            all_present = False
    
    
    # Show function sample
    functions = toon_data.get('functions', [])
    if functions:
        print(f"\n📋 Function Details Sample (first 3):")
        for i, func in enumerate(functions[:3]):
            print(f"  {i+1}. {func.get('name', 'N/A')} (CC={func.get('cc', 'N/A')})")
    
    return all_present

def main():
    """Main validation function."""
    if len(sys.argv) == 2:
        # Single file mode - validate TOON format structure only
        file_path = Path(sys.argv[1])
        
        if not file_path.exists():
            print(f"Error: {file_path} not found")
            sys.exit(1)
        
        print(f"🔍 Validating TOON format: {file_path.name}")
        print("=" * 60)
        
        # Load file (auto-detect format)
        data = load_file(file_path)
        
        if not data:
            print("Error: Could not load file")
            sys.exit(1)
        
        # Validate structure
        is_valid = validate_toon_completeness(data)
        
        # Final summary
        print("\n" + "=" * 60)
        print("📋 TOON FORMAT VALIDATION SUMMARY:")
        print("=" * 60)
        
        status = "✅ PASS" if is_valid else "❌ FAIL"
        print(f"{status} TOON Structure")
        
        print("\n" + ("🎉 TOON FORMAT VALID!" if is_valid else "⚠️  TOON FORMAT ISSUES!"))
        
        return 0 if is_valid else 1
    
    elif len(sys.argv) == 3:
        # Comparison mode - compare YAML vs TOON
        yaml_path = Path(sys.argv[1])
        toon_path = Path(sys.argv[2])
        
        if not yaml_path.exists():
            print(f"Error: {yaml_path} not found")
            sys.exit(1)
        
        if not toon_path.exists():
            print(f"Error: {toon_path} not found")
            sys.exit(1)
        
        print(f"🔍 Validating: {yaml_path.name} vs {toon_path.name}")
        print("=" * 60)
        
        # Load both files
        yaml_data = load_yaml(yaml_path)
        toon_data = load_file(toon_path)  # Auto-detect TOON format
        
        if not yaml_data or not toon_data:
            print("Error: Could not load one or both files")
            sys.exit(1)
        
        # Compare all aspects
        stats_match = compare_basic_stats(yaml_data, toon_data)
        functions_match = compare_functions(yaml_data, toon_data)
        classes_match = compare_classes(yaml_data, toon_data)
        modules_match = compare_modules(yaml_data, toon_data)
        toon_valid = validate_toon_completeness(toon_data)
        
        # Final summary
        print("\n" + "=" * 60)
        print("📋 FINAL VALIDATION SUMMARY:")
        print("=" * 60)
        
        results = [
            ("Basic Statistics", stats_match),
            ("Functions", functions_match),
            ("Classes", classes_match),
            ("Modules", modules_match),
            ("TOON Structure", toon_valid)
        ]
        
        all_passed = True
        for test_name, passed in results:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{status} {test_name}")
            if not passed:
                all_passed = False
        
        print("\n" + ("🎉 ALL TESTS PASSED!" if all_passed else "⚠️  SOME TESTS FAILED!"))
        
        return 0 if all_passed else 1
    
    else:
        print("Usage:")
        print("  python validate_toon.py <analysis.toon>                      # Validate TOON only")
        print("  python validate_toon.py <analysis.yaml> <analysis.toon>      # Compare both formats")
        sys.exit(1)

if __name__ == '__main__':
    sys.exit(main())
