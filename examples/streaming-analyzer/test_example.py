#!/usr/bin/env python3
"""
Simple test script to verify streaming analyzer works.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all streaming analyzer components can be imported."""
    try:
        from code2llm.core.streaming_analyzer import (
            StreamingAnalyzer, 
            STRATEGY_QUICK, 
            STRATEGY_STANDARD, 
            STRATEGY_DEEP,
            StreamingIncrementalAnalyzer
        )
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_basic_analysis():
    """Test basic streaming analysis."""
    try:
        from code2llm.core.streaming_analyzer import StreamingAnalyzer, STRATEGY_QUICK
        
        analyzer = StreamingAnalyzer(strategy=STRATEGY_QUICK)
        
        # Test with sample project
        results = list(analyzer.analyze_streaming("sample_project"))
        
        if results:
            final = results[-1]
            if final['type'] == 'complete':
                print(f"✅ Analysis completed in {final['elapsed_seconds']:.2f}s")
                print(f"   Files: {final['processed_files']}/{final['total_files']}")
                return True
        
        print("❌ No results from analysis")
        return False
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return False

def main():
    """Run tests."""
    print("🧪 Streaming Analyzer Test")
    print("=" * 40)
    
    # Change to demo directory
    import os
    os.chdir(Path(__file__).parent)
    
    tests = [
        ("Import Test", test_imports),
        ("Basic Analysis Test", test_basic_analysis),
    ]
    
    passed = 0
    total = len(tests)
    
    for name, test in tests:
        print(f"\n{name}:")
        if test():
            passed += 1
        else:
            print(f"   ❌ {name} failed")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Streaming analyzer is working correctly.")
        print("\nNext steps:")
        print("1. Try CLI commands:")
        print("   /usr/bin/python3 -m code2llm sample_project --strategy quick")
        print("   /usr/bin/python3 -m code2llm sample_project --strategy standard -v")
        print("   /usr/bin/python3 -m code2llm sample_project --strategy deep")
        print("\n2. Check output in code2llm_output/")
        return 0
    else:
        print("❌ Some tests failed. Check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
