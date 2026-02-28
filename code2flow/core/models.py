from dataclasses import dataclass, field, asdict
from typing import List, Dict, Set, Optional, Any
from pathlib import Path


class BaseModel:
    """Base class for models with automated serialization."""
    def to_dict(self, compact: bool = True) -> dict:
        """Convert to dictionary using dataclasses.asdict with filtering."""
        data = asdict(self)
        if compact:
            return self._filter_compact(data)
        return data

    def _filter_compact(self, data: Any) -> Any:
        """Recursively filter out None and empty collections if compact."""
        if isinstance(data, dict):
            return {
                k: self._filter_compact(v) 
                for k, v in data.items() 
                if v is not None and (not isinstance(v, (list, dict, set)) or len(v) > 0)
            }
        elif isinstance(data, (list, tuple, set)):
            return [self._filter_compact(v) for v in data]
        return data


@dataclass
class FlowNode(BaseModel):
    """Represents a node in the control flow graph."""
    id: str
    type: str  # FUNC, CALL, IF, FOR, WHILE, ASSIGN, RETURN, ENTRY, EXIT
    label: str
    function: Optional[str] = None
    file: Optional[str] = None
    line: Optional[int] = None
    column: Optional[int] = None
    conditions: List[str] = field(default_factory=list)
    data_flow: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FlowEdge(BaseModel):
    """Represents an edge in the control flow graph."""
    source: str
    target: str
    edge_type: str = "control"  # control, data, call
    label: Optional[str] = None
    conditions: List[str] = field(default_factory=list)


@dataclass
class FunctionInfo(BaseModel):
    """Information about a function/method."""
    name: str
    qualified_name: str
    file: str
    line: int
    column: int = 0
    module: str = ""
    class_name: Optional[str] = None
    is_method: bool = False
    is_private: bool = False
    is_property: bool = False
    docstring: Optional[str] = None
    args: List[str] = field(default_factory=list)
    returns: Optional[str] = None
    decorators: List[str] = field(default_factory=list)
    
    # CFG info
    cfg_entry: Optional[str] = None
    cfg_exit: Optional[str] = None
    cfg_nodes: List[str] = field(default_factory=list)
    calls: List[str] = field(default_factory=list)
    called_by: List[str] = field(default_factory=list)
    
    # Advanced metrics (Sprint 3)
    complexity: Dict[str, Any] = field(default_factory=dict) # Cyclomatic, Cognitive
    centrality: float = 0.0 # Betweenness Centrality
    reachability: str = "unknown" # reachable, unreachable, unknown


@dataclass
class ClassInfo(BaseModel):
    """Information about a class."""
    name: str
    qualified_name: str
    file: str
    line: int
    module: str = ""
    bases: List[str] = field(default_factory=list)
    methods: List[str] = field(default_factory=list)
    docstring: Optional[str] = None
    is_state_machine: bool = False


@dataclass
class ModuleInfo(BaseModel):
    """Information about a module/package."""
    name: str
    file: str
    is_package: bool = False
    imports: List[str] = field(default_factory=list)
    functions: List[str] = field(default_factory=list)
    classes: List[str] = field(default_factory=list)


@dataclass
class Pattern(BaseModel):
    """Detected behavioral pattern."""
    name: str
    type: str  # recursion, state_machine, factory, singleton, strategy, loop
    confidence: float  # 0.0 to 1.0
    functions: List[str] = field(default_factory=list)
    entry_points: List[str] = field(default_factory=list)
    exit_points: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CodeSmell(BaseModel):
    """Represents a detected code smell."""
    name: str
    type: str  # god_function, feature_envy, etc.
    file: str
    line: int
    severity: float  # 0.0 to 1.0
    description: str
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Mutation(BaseModel):
    """Represents a mutation of a variable/object."""
    variable: str
    file: str
    line: int
    type: str  # assign, aug_assign, method_call
    scope: str
    context: str


@dataclass
class DataFlow(BaseModel):
    """Represents data flow for a variable."""
    variable: str
    dependencies: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnalysisResult(BaseModel):
    """Complete analysis result for a project."""
    project_path: str = ""
    analysis_mode: str = "static"
    stats: Dict[str, int] = field(default_factory=dict)
    
    # Graph data
    nodes: Dict[str, FlowNode] = field(default_factory=dict)
    edges: List[FlowEdge] = field(default_factory=list)
    
    # Code structure
    modules: Dict[str, ModuleInfo] = field(default_factory=dict)
    classes: Dict[str, ClassInfo] = field(default_factory=dict)
    functions: Dict[str, FunctionInfo] = field(default_factory=dict)
    
    # Analysis results
    patterns: List[Pattern] = field(default_factory=list)
    call_graph: Dict[str, List[str]] = field(default_factory=list)
    entry_points: List[str] = field(default_factory=list)
    data_flows: Dict[str, DataFlow] = field(default_factory=dict)
    
    # Refactoring data
    metrics: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    smells: List[CodeSmell] = field(default_factory=list)
    coupling: Dict[str, Any] = field(default_factory=dict)
    mutations: List[Mutation] = field(default_factory=list)
    
    def get_function_count(self) -> int:
        """Get total function count."""
        return len(self.functions)
    
    def get_class_count(self) -> int:
        """Get total class count."""
        return len(self.classes)
    
    def get_node_count(self) -> int:
        """Get total CFG node count."""
        return len(self.nodes)
    
    def get_edge_count(self) -> int:
        """Get total edge count."""
        return len(self.edges)
