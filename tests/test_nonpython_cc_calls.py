"""Regression tests for non-Python cyclomatic complexity and call graph extraction.

Verifies that TypeScript, JavaScript, Go, Rust, and Java files get proper
CC values (not all zeros) and call graph edges extracted.
"""

import tempfile
from pathlib import Path
from code2llm.core.analyzer import ProjectAnalyzer
from code2llm.core.config import Config, FAST_CONFIG


class TestTypeScriptComplexityAndCalls:
    """Verify TS/JS files get CC > 0 and call edges."""

    TS_CODE = """\
import { Logger } from './logger';

class UserService {
    private users: any[] = [];

    constructor() {
        this.users = [];
    }

    addUser(user: any): void {
        if (user && user.name) {
            if (user.age > 0) {
                this.users.push(user);
            } else {
                throw new Error('invalid age');
            }
        }
    }

    findUser(id: number): any {
        for (const u of this.users) {
            if (u.id === id) {
                return u;
            }
        }
        return null;
    }

    processAll(): void {
        for (const u of this.users) {
            if (u.active || u.admin) {
                this.notify(u);
            }
        }
    }

    notify(user: any): void {
        console.log(user.name);
    }
}

function initService(): UserService {
    const svc = new UserService();
    return svc;
}

export function main(): void {
    const svc = initService();
    if (svc) {
        svc.processAll();
    }
}
"""

    def _analyze(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            ts_file = Path(tmpdir) / "user_service.ts"
            ts_file.write_text(self.TS_CODE)
            analyzer = ProjectAnalyzer(FAST_CONFIG)
            return analyzer.analyze_project(tmpdir)

    def test_ts_functions_detected(self):
        result = self._analyze()
        func_names = {f.name for f in result.functions.values()}
        # Should detect class methods (shorthand syntax) + standalone functions
        assert 'addUser' in func_names, f"addUser not found in {func_names}"
        assert 'findUser' in func_names, f"findUser not found in {func_names}"
        assert 'processAll' in func_names, f"processAll not found in {func_names}"
        assert 'notify' in func_names, f"notify not found in {func_names}"
        assert 'initService' in func_names, f"initService not found in {func_names}"
        assert 'main' in func_names, f"main not found in {func_names}"

    def test_ts_complexity_not_zero(self):
        result = self._analyze()
        ccs = {}
        for name, fi in result.functions.items():
            cc = fi.complexity.get('cyclomatic_complexity', 0)
            ccs[fi.name] = cc

        # addUser has if/if/else → CC should be > 1
        assert ccs.get('addUser', 0) > 1, f"addUser CC should be > 1, got {ccs.get('addUser')}"
        # findUser has for/if → CC > 1
        assert ccs.get('findUser', 0) > 1, f"findUser CC should be > 1, got {ccs.get('findUser')}"
        # processAll has for/if/|| → CC > 1
        assert ccs.get('processAll', 0) > 1, f"processAll CC should be > 1, got {ccs.get('processAll')}"
        # notify is trivial → CC = 1
        assert ccs.get('notify', 0) >= 1, f"notify CC should be >= 1, got {ccs.get('notify')}"

    def test_ts_calls_extracted(self):
        result = self._analyze()
        all_calls = {}
        for name, fi in result.functions.items():
            simple_calls = [c.rsplit('.', 1)[-1] for c in fi.calls]
            all_calls[fi.name] = simple_calls

        # processAll calls notify
        assert 'notify' in all_calls.get('processAll', []), \
            f"processAll should call notify, got {all_calls.get('processAll')}"
        # main calls initService
        assert 'initService' in all_calls.get('main', []), \
            f"main should call initService, got {all_calls.get('main')}"

    def test_ts_cc_avg_not_zero(self):
        result = self._analyze()
        total_cc = sum(
            fi.complexity.get('cyclomatic_complexity', 0)
            for fi in result.functions.values()
        )
        count = len(result.functions)
        assert count > 0
        avg = total_cc / count
        assert avg > 1.0, f"Average CC should be > 1.0 for non-trivial code, got {avg:.2f}"


class TestGoComplexityAndCalls:
    """Verify Go files get CC > 0."""

    GO_CODE = """\
package main

import "fmt"

type Server struct {
    port int
}

func (s *Server) Start() error {
    if s.port <= 0 {
        return fmt.Errorf("invalid port")
    }
    for i := 0; i < 3; i++ {
        if i > 1 {
            fmt.Println("retrying")
        }
    }
    return nil
}

func NewServer(port int) *Server {
    return &Server{port: port}
}

func main() {
    s := NewServer(8080)
    if err := s.Start(); err != nil {
        fmt.Println(err)
    }
}
"""

    def _analyze(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            go_file = Path(tmpdir) / "main.go"
            go_file.write_text(self.GO_CODE)
            analyzer = ProjectAnalyzer(FAST_CONFIG)
            return analyzer.analyze_project(tmpdir)

    def test_go_complexity_not_zero(self):
        result = self._analyze()
        ccs = {fi.name: fi.complexity.get('cyclomatic_complexity', 0)
               for fi in result.functions.values()}
        # Start has if/for/if → CC > 1
        assert ccs.get('Start', 0) > 1, f"Start CC should be > 1, got {ccs.get('Start')}"
        # main has if → CC > 1
        assert ccs.get('main', 0) > 1, f"main CC should be > 1, got {ccs.get('main')}"

    def test_go_calls_extracted(self):
        result = self._analyze()
        all_calls = {}
        for fi in result.functions.values():
            all_calls[fi.name] = [c.rsplit('.', 1)[-1] for c in fi.calls]
        # main calls NewServer
        assert 'NewServer' in all_calls.get('main', []), \
            f"main should call NewServer, got {all_calls.get('main')}"


class TestRustComplexityAndCalls:
    """Verify Rust files get CC > 0."""

    RUST_CODE = """\
use std::collections::HashMap;

struct Config {
    values: HashMap<String, String>,
}

impl Config {
    fn get(&self, key: &str) -> Option<&String> {
        if key.is_empty() {
            return None;
        }
        self.values.get(key)
    }

    fn set(&mut self, key: &str, value: &str) {
        if key.is_empty() || value.is_empty() {
            return;
        }
        self.values.insert(key.to_string(), value.to_string());
    }
}

fn load_config() -> Config {
    Config { values: HashMap::new() }
}

fn main() {
    let mut cfg = load_config();
    cfg.set("key", "value");
    if let Some(v) = cfg.get("key") {
        println!("{}", v);
    }
}
"""

    def _analyze(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            rs_file = Path(tmpdir) / "main.rs"
            rs_file.write_text(self.RUST_CODE)
            analyzer = ProjectAnalyzer(FAST_CONFIG)
            return analyzer.analyze_project(tmpdir)

    def test_rust_complexity_not_zero(self):
        result = self._analyze()
        ccs = {fi.name: fi.complexity.get('cyclomatic_complexity', 0)
               for fi in result.functions.values()}
        # set has if/|| → CC > 1
        assert ccs.get('set', 0) > 1, f"set CC should be > 1, got {ccs.get('set')}"
        # get has if → CC > 1
        assert ccs.get('get', 0) > 1, f"get CC should be > 1, got {ccs.get('get')}"


class TestJavaComplexityAndCalls:
    """Verify Java files get CC > 0."""

    JAVA_CODE = """\
import java.util.List;
import java.util.ArrayList;

public class UserService {
    private List<String> users;

    public UserService() {
        this.users = new ArrayList<>();
    }

    public void addUser(String name) {
        if (name != null && !name.isEmpty()) {
            users.add(name);
        }
    }

    public String findUser(String prefix) {
        for (String u : users) {
            if (u.startsWith(prefix)) {
                return u;
            }
        }
        return null;
    }

    public int countActive(boolean includeAdmin) {
        int count = 0;
        for (String u : users) {
            if (u.startsWith("active") || (includeAdmin && u.startsWith("admin"))) {
                count++;
            }
        }
        return count;
    }
}
"""

    def _analyze(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            java_file = Path(tmpdir) / "UserService.java"
            java_file.write_text(self.JAVA_CODE)
            analyzer = ProjectAnalyzer(FAST_CONFIG)
            return analyzer.analyze_project(tmpdir)

    def test_java_complexity_not_zero(self):
        result = self._analyze()
        ccs = {fi.name: fi.complexity.get('cyclomatic_complexity', 0)
               for fi in result.functions.values()}
        # addUser has if/&& → CC > 1
        assert ccs.get('addUser', 0) > 1, f"addUser CC should be > 1, got {ccs.get('addUser')}"
        # findUser has for/if → CC > 1
        assert ccs.get('findUser', 0) > 1, f"findUser CC should be > 1, got {ccs.get('findUser')}"
        # countActive has for/if/||/&& → CC > 1
        assert ccs.get('countActive', 0) > 1, f"countActive CC should be > 1, got {ccs.get('countActive')}"

    def test_java_calls_extracted(self):
        result = self._analyze()
        # At least some calls should be detected
        total_calls = sum(len(fi.calls) for fi in result.functions.values())
        assert total_calls > 0, "Java should have some call edges detected"
