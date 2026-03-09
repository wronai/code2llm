"""End-to-end tests for multi-language analysis support.

Tests that code2llm correctly analyzes projects with multiple programming languages
including TypeScript, JavaScript, Go, Rust, Java, and others.
"""

import tempfile
import os
from pathlib import Path
from code2llm.core.analyzer import ProjectAnalyzer
from code2llm.core.config import Config, FAST_CONFIG


class TestMultiLanguageE2E:
    """E2E tests for multi-language project analysis."""

    def test_typescript_analysis(self):
        """Test TypeScript file analysis."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a TypeScript file
            ts_file = Path(tmpdir) / "main.ts"
            ts_file.write_text("""
import { logger } from './utils';

class AppComponent {
    private name: string;
    
    constructor(name: string) {
        this.name = name;
    }
    
    public render(): void {
        console.log(`Hello ${this.name}`);
    }
}

function initApp(): void {
    const app = new AppComponent('Test');
    app.render();
}

export { AppComponent, initApp };
""")
            
            analyzer = ProjectAnalyzer(FAST_CONFIG)
            result = analyzer.analyze_project(tmpdir)
            
            assert len(result.functions) >= 2, f"Expected at least 2 functions, got {len(result.functions)}"
            assert len(result.classes) >= 1, f"Expected at least 1 class, got {len(result.classes)}"
            
            # Check if TypeScript functions are detected
            func_names = [f.name for f in result.functions.values()]
            assert 'initApp' in func_names or 'render' in func_names, \
                f"Expected TypeScript functions, got {func_names}"

    def test_javascript_analysis(self):
        """Test JavaScript file analysis."""
        with tempfile.TemporaryDirectory() as tmpdir:
            js_file = Path(tmpdir) / "app.js"
            js_file.write_text("""
const utils = require('./utils');

class UserService {
    constructor() {
        this.users = [];
    }
    
    addUser(user) {
        this.users.push(user);
    }
    
    getUser(id) {
        return this.users.find(u => u.id === id);
    }
}

function setupServer() {
    const service = new UserService();
    return service;
}

module.exports = { UserService, setupServer };
""")
            
            analyzer = ProjectAnalyzer(FAST_CONFIG)
            result = analyzer.analyze_project(tmpdir)
            
            assert len(result.functions) >= 1, f"Expected at least 1 function, got {len(result.functions)}"
            assert len(result.classes) >= 1, f"Expected at least 1 class, got {len(result.classes)}"

    def test_go_analysis(self):
        """Test Go file analysis."""
        with tempfile.TemporaryDirectory() as tmpdir:
            go_file = Path(tmpdir) / "main.go"
            go_file.write_text("""
package main

import "fmt"

type User struct {
    Name string
    Age  int
}

func (u *User) Greet() {
    fmt.Printf("Hello, I'm %s\\n", u.Name)
}

func NewUser(name string, age int) *User {
    return &User{Name: name, Age: age}
}

func main() {
    user := NewUser("Alice", 30)
    user.Greet()
}
""")
            
            analyzer = ProjectAnalyzer(FAST_CONFIG)
            result = analyzer.analyze_project(tmpdir)
            
            assert len(result.functions) >= 2, f"Expected at least 2 functions, got {len(result.functions)}"
            assert len(result.classes) >= 1, f"Expected at least 1 struct, got {len(result.classes)}"

    def test_rust_analysis(self):
        """Test Rust file analysis."""
        with tempfile.TemporaryDirectory() as tmpdir:
            rs_file = Path(tmpdir) / "main.rs"
            rs_file.write_text("""
use std::collections::HashMap;

struct Config {
    name: String,
    values: HashMap<String, String>,
}

impl Config {
    fn new(name: &str) -> Self {
        Config {
            name: name.to_string(),
            values: HashMap::new(),
        }
    }
    
    fn get(&self, key: &str) -> Option<&String> {
        self.values.get(key)
    }
}

fn load_config() -> Config {
    Config::new("default")
}

fn main() {
    let config = load_config();
}
""")
            
            analyzer = ProjectAnalyzer(FAST_CONFIG)
            result = analyzer.analyze_project(tmpdir)
            
            assert len(result.functions) >= 2, f"Expected at least 2 functions, got {len(result.functions)}"
            assert len(result.classes) >= 1, f"Expected at least 1 struct, got {len(result.classes)}"

    def test_java_analysis(self):
        """Test Java file analysis."""
        with tempfile.TemporaryDirectory() as tmpdir:
            java_file = Path(tmpdir) / "UserService.java"
            java_file.write_text("""
import java.util.List;
import java.util.ArrayList;

public class UserService {
    private List<User> users;
    
    public UserService() {
        this.users = new ArrayList<>();
    }
    
    public void addUser(User user) {
        users.add(user);
    }
    
    public User getUser(int id) {
        return users.stream()
            .filter(u -> u.getId() == id)
            .findFirst()
            .orElse(null);
    }
}

class User {
    private int id;
    private String name;
    
    public User(int id, String name) {
        this.id = id;
        this.name = name;
    }
    
    public int getId() {
        return id;
    }
}
""")
            
            analyzer = ProjectAnalyzer(FAST_CONFIG)
            result = analyzer.analyze_project(tmpdir)
            
            assert len(result.functions) >= 2, f"Expected at least 2 functions, got {len(result.functions)}"
            assert len(result.classes) >= 2, f"Expected at least 2 classes, got {len(result.classes)}"

    def test_multilanguage_project(self):
        """Test analysis of project with multiple languages."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Python file
            (tmpdir / "app.py").write_text("""
from typing import List

class DataProcessor:
    def process(self, data: List[str]) -> List[str]:
        return [d.upper() for d in data]

def main():
    processor = DataProcessor()
    result = processor.process(["a", "b", "c"])
""")
            
            # TypeScript file
            (tmpdir / "frontend.ts").write_text("""
interface ApiResponse {
    data: string[];
}

class ApiClient {
    async fetchData(): Promise<ApiResponse> {
        return { data: [] };
    }
}

function initClient(): ApiClient {
    return new ApiClient();
}
""")
            
            # Go file
            (tmpdir / "server.go").write_text("""
package main

import "net/http"

type Server struct {
    port int
}

func (s *Server) Start() error {
    return http.ListenAndServe(":8080", nil)
}

func NewServer(port int) *Server {
    return &Server{port: port}
}
""")
            
            analyzer = ProjectAnalyzer(FAST_CONFIG)
            result = analyzer.analyze_project(tmpdir)
            
            # Should detect entities from all languages
            assert len(result.functions) >= 3, f"Expected at least 3 functions, got {len(result.functions)}"
            assert len(result.classes) >= 3, f"Expected at least 3 classes, got {len(result.classes)}"

    def test_language_detection_in_output(self):
        """Test that language detection works in output files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Create files of different languages
            (tmpdir / "main.ts").write_text("const x = 1;")
            (tmpdir / "app.js").write_text("const y = 2;")
            (tmpdir / "utils.py").write_text("z = 3")
            
            analyzer = ProjectAnalyzer(FAST_CONFIG)
            result = analyzer.analyze_project(tmpdir)
            
            # All modules should be present
            assert len(result.modules) >= 3, f"Expected at least 3 modules, got {len(result.modules)}"

    def test_excluded_directories_not_analyzed(self):
        """Test that node_modules and similar are excluded."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Create a valid source file
            (tmpdir / "app.ts").write_text("function main() { console.log('hello'); }")
            
            # Create node_modules with a file
            node_modules = tmpdir / "node_modules"
            node_modules.mkdir()
            (node_modules / "library.ts").write_text("function lib() { return 42; }")
            
            analyzer = ProjectAnalyzer(FAST_CONFIG)
            result = analyzer.analyze_project(tmpdir)
            
            # Should analyze app.ts but not node_modules/library.ts
            assert len(result.functions) >= 1
            
            # Check that node_modules path is not in results
            for mod in result.modules.values():
                assert "node_modules" not in mod.file, \
                    f"node_modules should be excluded: {mod.file}"


if __name__ == "__main__":
    # Run tests
    test = TestMultiLanguageE2E()
    
    print("Running test_typescript_analysis...")
    test.test_typescript_analysis()
    print("PASSED")
    
    print("Running test_javascript_analysis...")
    test.test_javascript_analysis()
    print("PASSED")
    
    print("Running test_go_analysis...")
    test.test_go_analysis()
    print("PASSED")
    
    print("Running test_rust_analysis...")
    test.test_rust_analysis()
    print("PASSED")
    
    print("Running test_java_analysis...")
    test.test_java_analysis()
    print("PASSED")
    
    print("Running test_multilanguage_project...")
    test.test_multilanguage_project()
    print("PASSED")
    
    print("Running test_language_detection_in_output...")
    test.test_language_detection_in_output()
    print("PASSED")
    
    print("Running test_excluded_directories_not_analyzed...")
    test.test_excluded_directories_not_analyzed()
    print("PASSED")
    
    print("\nAll E2E tests passed!")
