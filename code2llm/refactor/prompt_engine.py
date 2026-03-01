"""Engine for generating refactoring prompts using Jinja2 templates."""
import os
import jinja2
import tiktoken
from tree_sitter import Language, Parser
import tree_sitter_python
from typing import List, Dict, Any, Optional
from ..core.models import AnalysisResult, CodeSmell

class PromptEngine:
    """Generate refactoring prompts from analysis results and detected smells."""
    
    def __init__(self, result: AnalysisResult, template_dir: Optional[str] = None):
        if template_dir is None:
            # Default to templates directory relative to this file
            template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
            
        self.result = result
        self.env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))
        
        # Initialize tiktoken for context management
        try:
            self.encoding = tiktoken.get_encoding("cl100k_base") # GPT-4/3.5-turbo encoding
        except Exception:
            self.encoding = None
            
        # Initialize tree-sitter for precision extraction
        try:
            self.PY_LANGUAGE = Language(tree_sitter_python.language())
            self.parser = Parser(self.PY_LANGUAGE)
        except Exception:
            self.parser = None
        
    def generate_prompts(self) -> Dict[str, str]:
        """Generate a prompt for each detected code smell."""
        prompts = {}
        
        for i, smell in enumerate(self.result.smells):
            prompt = self._generate_prompt_for_smell(smell)
            if prompt:
                # Truncate prompt if it exceeds token limit (e.g., 4000 tokens)
                if self.encoding:
                    tokens = self.encoding.encode(prompt)
                    if len(tokens) > 4000:
                        prompt = self.encoding.decode(tokens[:3800]) + "\n\n... (prompt truncated due to length) ..."
                
                # Use a unique name for each prompt
                filename = f"{i+1:02d}_{smell.type}_{smell.name.lower().replace(' ', '_').replace(':', '')}.md"
                prompts[filename] = prompt
        return prompts
        
    def _generate_prompt_for_smell(self, smell: CodeSmell) -> Optional[str]:
        """Generate a single prompt from a CodeSmell."""
        template_name = self._get_template_for_type(smell.type)
        if not template_name:
            return None
            
        try:
            template = self.env.get_template(template_name)
            context = self._build_context_for_smell(smell)
            return template.render(**context)
        except Exception as e:
            print(f"Error generating prompt for {smell.name}: {e}")
            return None
            
    def _get_template_for_type(self, smell_type: str) -> Optional[str]:
        """Map smell type to Jinja2 template filename."""
        mapping = {
            "god_function": "extract_method.md",
            "feature_envy": "move_method.md",
            "data_clump": "move_method.md", 
            "shotgun_surgery": "extract_method.md",
            "bottleneck": "extract_method.md",
            "circular_dependency": "move_method.md"
        }
        return mapping.get(smell_type)
        
    def _build_context_for_smell(self, smell: CodeSmell) -> Dict[str, Any]:
        """Prepare context data for the Jinja2 template."""
        # Extract source code for context
        source_code = self._get_source_context(smell.file, smell.line)
        
        # Prepare metrics
        metrics = self.result.metrics.get(smell.name.split(': ')[-1], {}) # Heuristic to find function name
        if not metrics and 'function' in smell.context:
            metrics = self.result.metrics.get(smell.context['function'], {})

        # Prepare mutations
        mutations = [m for m in self.result.mutations if m.scope in (smell.name.split(': ')[-1], smell.context.get('function'))]
        mutations_summary = f"{len(mutations)} modifications recorded: {', '.join(set([m.variable for m in mutations[:5]]))}..."

        context = {
            "target_function": smell.name.split(': ')[-1],
            "reason": smell.description,
            "metrics": metrics,
            "mutations_context": mutations_summary,
            "source_file": smell.file,
            "start_line": smell.line,
            "end_line": smell.line + 20, # Heuristic: end of function or next 20 lines
            "source_code": source_code,
            "instruction": self._get_instruction_for_smell(smell),
            # move_method specific
            "source_module": smell.file.split('/')[-1].replace('.py', ''),
            "target_module": smell.context.get('foreign_mutations', ["other_module"])[0].split('.')[0] if smell.type == "feature_envy" else "other_module",
            "foreign_mutations": ", ".join(smell.context.get('foreign_mutations', [])),
            "foreign_mutations_context": f"This code mutates state in {', '.join(set([v.split('.')[0] for v in smell.context.get('foreign_mutations', []) if '.' in v]))}",
            "dependencies": ", ".join(set([m.variable for m in mutations if '.' in m.variable])),
            "reachability": self.result.functions.get(smell.name.split(': ')[-1], {}).reachability if hasattr(self.result.functions.get(smell.name.split(': ')[-1]), 'reachability') else "unknown"
        }
        return context

    def _get_source_context(self, file_path: str, start_line: int, max_lines: int = 50) -> str:
        """Read source code lines from a file."""
        if not os.path.exists(file_path):
            return "# Source file not found."
            
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
            # If tree-sitter is available, use it to accurately find function boundaries
            if self.parser and "method" not in file_path: # simplified check
                tree = self.parser.parse(bytes(content, "utf8"))
                root_node = tree.root_node
                
                # Simple function extraction using tree-sitter
                # (Ideally we'd search for the function node at start_line)
                lines = content.splitlines()
                start = max(0, start_line - 1)
                end = min(len(lines), start + max_lines)
                return "\n".join(lines[start:end])
            else:
                lines = content.splitlines()
                start = max(0, start_line - 1)
                end = min(len(lines), start + max_lines)
                return "\n".join(lines[start:end])
        except Exception as e:
            return f"# Error reading source: {e}"

    def _get_instruction_for_smell(self, smell: CodeSmell) -> str:
        """Generate specific instruction based on smell type."""
        if smell.type == "god_function":
            return f"Wyekstrahuj mniejsze, spójne metody z funkcji {smell.name.split(': ')[-1]}. Skup się na wydzieleniu operacji o największej liczbie mutacji."
        elif smell.type == "feature_envy":
            return f"Przenieś metodę {smell.name.split(': ')[-1]} do modułu, który posiada większość używanych w niej danych. Zmniejsz coupling między modułami."
        elif smell.type == "bottleneck":
            return f"Funkcja {smell.name.split(': ')[-1]} jest wąskim gardłem strukturalnym. Wyekstrahuj z niej niezależne części pomocnicze, aby ułatwić zrozumienie przepływu."
        elif smell.type == "circular_dependency":
            return f"Wykryto cykl zależności. Przenieś część logiki do nowego modułu lub użyj interfejsu, aby przerwać cykl."
        return "Zrefaktoryzuj ten fragment kodu, aby poprawić jego strukturę i zmniejszyć złożoność."
