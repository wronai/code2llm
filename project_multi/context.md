# System Architecture Analysis

## Overview

- **Project**: /home/tom/github/wronai/nlp2cmd
- **Analysis Mode**: static
- **Total Functions**: 508
- **Total Classes**: 63
- **Modules**: 123
- **Entry Points**: 0

## Architecture by Module

### 03_integrations.web_development.nlp2cmd_web_controller
- **Functions**: 52
- **Classes**: 8
- **File**: `nlp2cmd_web_controller.py`

### examples.04_domain_specific._dynamic_orchestrator
- **Functions**: 35
- **Classes**: 3
- **File**: `_dynamic_orchestrator.py`

### 03_integrations.toon_format.comparison_demo
- **Functions**: 16
- **Classes**: 2
- **File**: `comparison_demo.py`

### examples.04_domain_specific.benchmark_nlp2cmd
- **Functions**: 14
- **Classes**: 2
- **File**: `benchmark_nlp2cmd.py`

### 04_domain_specific._demo_helpers
- **Functions**: 12
- **File**: `_demo_helpers.py`

### 04_domain_specific.data_science.dsl_demo
- **Functions**: 11
- **File**: `dsl_demo.py`

### 04_domain_specific.polish_llm_integration.example_pdf_search
- **Functions**: 9
- **Classes**: 2
- **File**: `example_pdf_search.py`

### 05_advanced_features.schema_driven_architecture.04_plan_executor.demo
- **Functions**: 9
- **Classes**: 2
- **File**: `demo.py`

### 04_domain_specific.energy.example
- **Functions**: 8
- **File**: `example.py`

### 04_domain_specific.smart_cities.example
- **Functions**: 8
- **File**: `example.py`

### 04_domain_specific.physics.example
- **Functions**: 8
- **File**: `example.py`

### 04_domain_specific.healthcare.example
- **Functions**: 8
- **File**: `example.py`

### 04_domain_specific.education.example
- **Functions**: 8
- **File**: `example.py`

### 04_domain_specific.polish_llm_integration.05_integration.demo
- **Functions**: 8
- **Classes**: 4
- **File**: `demo.py`

### 03_integrations.web_development.web_app_example
- **Functions**: 8
- **Classes**: 3
- **File**: `web_app_example.py`

### 03_integrations.toon_format.practical_usage
- **Functions**: 8
- **Classes**: 1
- **File**: `practical_usage.py`

### 09_online_drawing.02_picsart_painting
- **Functions**: 7
- **File**: `02_picsart_painting.py`

### 04_domain_specific.logistics.example
- **Functions**: 7
- **File**: `example.py`

### 04_domain_specific.finance.example
- **Functions**: 7
- **File**: `example.py`

### 04_domain_specific.bioinformatics.complete_examples
- **Functions**: 7
- **File**: `complete_examples.py`

## Key Entry Points

Main execution flows into the system:

## Process Flows

Key execution flows identified:

## Key Classes

### _dynamic_orchestrator.DynamicOrchestrator
> LLM-driven browser automation engine.

No hardcoded code presets — everything is generated at runtim
- **Methods**: 32
- **Key Methods**: _dynamic_orchestrator.DynamicOrchestrator.__init__, _dynamic_orchestrator.DynamicOrchestrator.router, _dynamic_orchestrator.DynamicOrchestrator.execute_task, _dynamic_orchestrator.DynamicOrchestrator._plan_task, _dynamic_orchestrator.DynamicOrchestrator._sanitize_plan, _dynamic_orchestrator.DynamicOrchestrator._heuristic_plan, _dynamic_orchestrator.DynamicOrchestrator._retry_code_cycle, _dynamic_orchestrator.DynamicOrchestrator._execute_with_retry, _dynamic_orchestrator.DynamicOrchestrator._repair_loop, _dynamic_orchestrator.DynamicOrchestrator._ask_llm_repair

### 03_integrations.web_development.nlp2cmd_web_controller.NLP2CMDWebController
> Main controller for NLP2CMD-powered web infrastructure.

This class orchestrates the deployment and 
- **Methods**: 30
- **Key Methods**: 03_integrations.web_development.nlp2cmd_web_controller.NLP2CMDWebController.__init__, 03_integrations.web_development.nlp2cmd_web_controller.NLP2CMDWebController.execute, 03_integrations.web_development.nlp2cmd_web_controller.NLP2CMDWebController._handle_deploy, 03_integrations.web_development.nlp2cmd_web_controller.NLP2CMDWebController._handle_configure, 03_integrations.web_development.nlp2cmd_web_controller.NLP2CMDWebController._handle_scale, 03_integrations.web_development.nlp2cmd_web_controller.NLP2CMDWebController._handle_status, 03_integrations.web_development.nlp2cmd_web_controller.NLP2CMDWebController._handle_stop, 03_integrations.web_development.nlp2cmd_web_controller.NLP2CMDWebController._handle_unknown, 03_integrations.web_development.nlp2cmd_web_controller.NLP2CMDWebController._execute_with_nlp2cmd, 03_integrations.web_development.nlp2cmd_web_controller.NLP2CMDWebController._try_llm_fallback

### 05_advanced_features.schema_driven_architecture.04_plan_executor.demo.PlanExecutor
> Wykonawca planu.
- **Methods**: 8
- **Key Methods**: 05_advanced_features.schema_driven_architecture.04_plan_executor.demo.PlanExecutor.__init__, 05_advanced_features.schema_driven_architecture.04_plan_executor.demo.PlanExecutor._mock_execute, 05_advanced_features.schema_driven_architecture.04_plan_executor.demo.PlanExecutor._mock_check_disk, 05_advanced_features.schema_driven_architecture.04_plan_executor.demo.PlanExecutor._mock_backup, 05_advanced_features.schema_driven_architecture.04_plan_executor.demo.PlanExecutor._mock_tests, 05_advanced_features.schema_driven_architecture.04_plan_executor.demo.PlanExecutor._mock_build, 05_advanced_features.schema_driven_architecture.04_plan_executor.demo.PlanExecutor.execute_step, 05_advanced_features.schema_driven_architecture.04_plan_executor.demo.PlanExecutor.execute_plan

### 03_integrations.toon_format.practical_usage.ToonDemo
> Demo class showing TOON usage patterns
- **Methods**: 7
- **Key Methods**: 03_integrations.toon_format.practical_usage.ToonDemo.__init__, 03_integrations.toon_format.practical_usage.ToonDemo._load_toon_data, 03_integrations.toon_format.practical_usage.ToonDemo.show_basic_usage, 03_integrations.toon_format.practical_usage.ToonDemo.show_advanced_usage, 03_integrations.toon_format.practical_usage.ToonDemo.show_real_world_examples, 03_integrations.toon_format.practical_usage.ToonDemo.show_integration_examples, 03_integrations.toon_format.practical_usage.ToonDemo.show_performance_tips

### 04_domain_specific.debugging.validation.ShellCommandValidator
> Walidator komend shell.
- **Methods**: 6
- **Key Methods**: 04_domain_specific.debugging.validation.ShellCommandValidator.__init__, 04_domain_specific.debugging.validation.ShellCommandValidator.get_test_cases, 04_domain_specific.debugging.validation.ShellCommandValidator.validate_command, 04_domain_specific.debugging.validation.ShellCommandValidator._calculate_similarity, 04_domain_specific.debugging.validation.ShellCommandValidator.validate_all, 04_domain_specific.debugging.validation.ShellCommandValidator.generate_report

### 03_integrations.toon_format.comparison_demo.SimpleToonParser
> Simplified TOON parser for demo
- **Methods**: 6
- **Key Methods**: 03_integrations.toon_format.comparison_demo.SimpleToonParser.__init__, 03_integrations.toon_format.comparison_demo.SimpleToonParser._parse_file, 03_integrations.toon_format.comparison_demo.SimpleToonParser.get_commands, 03_integrations.toon_format.comparison_demo.SimpleToonParser.get_config, 03_integrations.toon_format.comparison_demo.SimpleToonParser.get_command_by_name, 03_integrations.toon_format.comparison_demo.SimpleToonParser.search_commands

### 04_domain_specific.polish_llm_integration.example_pdf_search.PolishPDFSearchLLM
> Integracja polskiego LLM do wyszukiwania plików PDF.
- **Methods**: 5
- **Key Methods**: 04_domain_specific.polish_llm_integration.example_pdf_search.PolishPDFSearchLLM.__init__, 04_domain_specific.polish_llm_integration.example_pdf_search.PolishPDFSearchLLM.generate_pdf_search_command, 04_domain_specific.polish_llm_integration.example_pdf_search.PolishPDFSearchLLM._generate_with_lite_llm, 04_domain_specific.polish_llm_integration.example_pdf_search.PolishPDFSearchLLM._generate_with_local_llm, 04_domain_specific.polish_llm_integration.example_pdf_search.PolishPDFSearchLLM._clean_command

### 03_integrations.toon_format.comparison_demo.OldSystemLoader
> Mock old system using separate JSON/YAML files
- **Methods**: 5
- **Key Methods**: 03_integrations.toon_format.comparison_demo.OldSystemLoader.__init__, 03_integrations.toon_format.comparison_demo.OldSystemLoader.load_command_schemas, 03_integrations.toon_format.comparison_demo.OldSystemLoader.load_config, 03_integrations.toon_format.comparison_demo.OldSystemLoader.get_command_by_name, 03_integrations.toon_format.comparison_demo.OldSystemLoader.search_commands

### 03_integrations.web_development.nlp2cmd_web_controller.DockerManager
> Manages Docker Compose operations and container lifecycle.
- **Methods**: 5
- **Key Methods**: 03_integrations.web_development.nlp2cmd_web_controller.DockerManager.__init__, 03_integrations.web_development.nlp2cmd_web_controller.DockerManager.start_services, 03_integrations.web_development.nlp2cmd_web_controller.DockerManager.get_container_status, 03_integrations.web_development.nlp2cmd_web_controller.DockerManager.show_logs, 03_integrations.web_development.nlp2cmd_web_controller.DockerManager.stop_services

### 03_integrations.web_development.nlp2cmd_web_controller.NLP2CMDWebAPI
> Example web API integration for NLP2CMD.

This class shows how to integrate NLP2CMD with web framewo
- **Methods**: 5
- **Key Methods**: 03_integrations.web_development.nlp2cmd_web_controller.NLP2CMDWebAPI.__init__, 03_integrations.web_development.nlp2cmd_web_controller.NLP2CMDWebAPI.process_command, 03_integrations.web_development.nlp2cmd_web_controller.NLP2CMDWebAPI.get_status, 03_integrations.web_development.nlp2cmd_web_controller.NLP2CMDWebAPI.get_history, 03_integrations.web_development.nlp2cmd_web_controller.NLP2CMDWebAPI.get_services

### 05_advanced_features.schema_driven_architecture.05_result_aggregator.demo.ResultAggregator
> Agregator wyników.
- **Methods**: 5
- **Key Methods**: 05_advanced_features.schema_driven_architecture.05_result_aggregator.demo.ResultAggregator.aggregate, 05_advanced_features.schema_driven_architecture.05_result_aggregator.demo.ResultAggregator._to_json, 05_advanced_features.schema_driven_architecture.05_result_aggregator.demo.ResultAggregator._to_yaml, 05_advanced_features.schema_driven_architecture.05_result_aggregator.demo.ResultAggregator._to_table, 05_advanced_features.schema_driven_architecture.05_result_aggregator.demo.ResultAggregator._to_markdown

### 04_domain_specific.debugging.10_advanced_validation.demo.AdvancedValidator
> Zaawansowany walidator komend.
- **Methods**: 4
- **Key Methods**: 04_domain_specific.debugging.10_advanced_validation.demo.AdvancedValidator.__init__, 04_domain_specific.debugging.10_advanced_validation.demo.AdvancedValidator.validate, 04_domain_specific.debugging.10_advanced_validation.demo.AdvancedValidator._calculate_similarity, 04_domain_specific.debugging.10_advanced_validation.demo.AdvancedValidator.summary

### 04_domain_specific.polish_llm_integration.01_pdf_extraction.demo.PDFExtractor
> Ekstraktor tekstu z PDF.
- **Methods**: 4
- **Key Methods**: 04_domain_specific.polish_llm_integration.01_pdf_extraction.demo.PDFExtractor.__init__, 04_domain_specific.polish_llm_integration.01_pdf_extraction.demo.PDFExtractor.extract_text, 04_domain_specific.polish_llm_integration.01_pdf_extraction.demo.PDFExtractor.extract_metadata, 04_domain_specific.polish_llm_integration.01_pdf_extraction.demo.PDFExtractor.batch_extract

### 04_domain_specific.polish_llm_integration.04_results_ranking.demo.ResultsRanker
> Ranks and filters search results.
- **Methods**: 4
- **Key Methods**: 04_domain_specific.polish_llm_integration.04_results_ranking.demo.ResultsRanker.__init__, 04_domain_specific.polish_llm_integration.04_results_ranking.demo.ResultsRanker.rank_results, 04_domain_specific.polish_llm_integration.04_results_ranking.demo.ResultsRanker.diversify_results, 04_domain_specific.polish_llm_integration.04_results_ranking.demo.ResultsRanker.get_top_k

### 08_llm_validation.benchmark_validator.CaseResult
- **Methods**: 4
- **Key Methods**: 08_llm_validation.benchmark_validator.CaseResult.verdict_correct, 08_llm_validation.benchmark_validator.CaseResult.consistent, 08_llm_validation.benchmark_validator.CaseResult.avg_latency_ms, 08_llm_validation.benchmark_validator.CaseResult.deterministic

### 04_domain_specific.polish_llm_integration.03_llm_search.demo.LLMSearcher
> Wyszukiwanie informacji za pomocą LLM.
- **Methods**: 4
- **Key Methods**: 04_domain_specific.polish_llm_integration.03_llm_search.demo.LLMSearcher.__init__, 04_domain_specific.polish_llm_integration.03_llm_search.demo.LLMSearcher.search, 04_domain_specific.polish_llm_integration.03_llm_search.demo.LLMSearcher._calculate_relevance, 04_domain_specific.polish_llm_integration.03_llm_search.demo.LLMSearcher._extract_matches

### 03_integrations.web_development.nlp2cmd_web_controller.OutputFileManager
> Manages saving generated configurations to files.
- **Methods**: 4
- **Key Methods**: 03_integrations.web_development.nlp2cmd_web_controller.OutputFileManager.__init__, 03_integrations.web_development.nlp2cmd_web_controller.OutputFileManager.save_docker_compose, 03_integrations.web_development.nlp2cmd_web_controller.OutputFileManager.save_service_config, 03_integrations.web_development.nlp2cmd_web_controller.OutputFileManager.save_deployment_plan

### 03_integrations.web_development.nlp2cmd_web_controller.NLCommandParser
> Parse natural language commands into structured actions.

Supports Polish and English commands for:

- **Methods**: 4
- **Key Methods**: 03_integrations.web_development.nlp2cmd_web_controller.NLCommandParser.parse, 03_integrations.web_development.nlp2cmd_web_controller.NLCommandParser._detect_intent, 03_integrations.web_development.nlp2cmd_web_controller.NLCommandParser._detect_service_type, 03_integrations.web_development.nlp2cmd_web_controller.NLCommandParser._extract_entities

### 04_domain_specific.polish_llm_integration.05_integration.demo.PDFSearchPipeline
> Pełny pipeline wyszukiwania w PDF.
- **Methods**: 3
- **Key Methods**: 04_domain_specific.polish_llm_integration.05_integration.demo.PDFSearchPipeline.__init__, 04_domain_specific.polish_llm_integration.05_integration.demo.PDFSearchPipeline.search_pdf, 04_domain_specific.polish_llm_integration.05_integration.demo.PDFSearchPipeline.batch_search

### 04_domain_specific.polish_llm_integration.02_text_chunking.demo.TextChunker
> Dzieli tekst na fragmenty odpowiednie dla LLM.
- **Methods**: 3
- **Key Methods**: 04_domain_specific.polish_llm_integration.02_text_chunking.demo.TextChunker.__init__, 04_domain_specific.polish_llm_integration.02_text_chunking.demo.TextChunker.chunk_text, 04_domain_specific.polish_llm_integration.02_text_chunking.demo.TextChunker.chunk_with_metadata

## Data Transformation Functions

Key functions that process and transform data:

### 04_domain_specific.data_science.dsl_demo.demo_process_management
> Demonstracja zarządzania procesami.
- **Output to**: 04_domain_specific.data_science.dsl_demo.run_query_group

### _dynamic_orchestrator.DynamicOrchestrator._step_validate
- **Output to**: self.context.get, step.get, self.context.get, StepResult, self.router.completion

### _dynamic_orchestrator._parse_json
> Robust JSON extraction from LLM output (handles markdown fences, preamble).
- **Output to**: text.strip, _dynamic_orchestrator._strip_code_fences, ValueError, json.loads, json.loads

### 04_domain_specific.debugging.validation.ShellCommandValidator.validate_command
> Waliduje pojedynczą komendę.
- **Output to**: time.time, self._calculate_similarity, self.generator.generate, hasattr, hasattr

### 04_domain_specific.debugging.validation.ShellCommandValidator.validate_all
> Waliduje wszystkie komendy.
- **Output to**: self.get_test_cases, print, print, _example_helpers.print_rule, enumerate

### 04_domain_specific.debugging.10_advanced_validation.demo.AdvancedValidator.validate
- **Output to**: self._calculate_similarity, ValidationResult, self.results.append

### 01_basics.docker_basics.file_repair.validate_file
> Validate a file and print results.
- **Output to**: path.read_text, print, print, _example_helpers.print_rule, registry.validate

### 01_basics.shell_fundamentals.environment_analysis.format_size
> Format size in human-readable format.

### 03_integrations.web_development.web_app_example.process_command
> Przetwarzaj komendę z języka naturalnego.
- **Output to**: app.post, CommandResponse, nlp_api.process_command, HTTPException, HTTPException

### 03_integrations.toon_format.comparison_demo.SimpleToonParser._parse_file
> Parse TOON file
- **Output to**: content.split, self.file_path.exists, print, open, f.read

### 03_integrations.toon_format.comparison_demo.demonstrate_llm_friendly_format
> Show how TOON format is LLM-friendly
- **Output to**: print, print, print, print, print

### 03_integrations.pipelines.infrastructure_health.mock_process_list
> Mock: System process list.

### 03_integrations.toon_format.14_batch_processing.demo.batch_validate
> Walidacja wsadowa komend.
- **Output to**: None.append, None.append, cmd.get

### 03_integrations.toon_format.08_memory_usage.demo.format_size
> Formatuje rozmiar w bajtach na czytelną formę.

### 03_integrations.web_development.nlp2cmd_web_controller.NLCommandParser.parse
> Parse natural language command.
- **Output to**: text.lower, self._detect_intent, self._detect_service_type, self._extract_entities

### 03_integrations.web_development.nlp2cmd_web_controller.NLP2CMDWebAPI.process_command
> Process command from web interface.

Returns JSON-serializable result.
- **Output to**: self.controller.execute, None.isoformat, datetime.now, None.isoformat, str

## Public API Surface

Functions exposed as public API (no underscore prefix):

- `01_basics.shell_fundamentals.environment_analysis.main` - 139 calls
- `10_online_code_editors.03_adaptive_code.main` - 131 calls
- `10_online_code_editors.02_mycompiler_run.main` - 114 calls
- `03_integrations.web_development.demo.demo_nlp_commands` - 106 calls
- `03_integrations.web_development.demo_batch.run_batch_demo` - 95 calls
- `09_online_drawing.03_adaptive_drawing.main` - 89 calls
- `05_advanced_features.schema_driven_architecture.end_to_end_demo.main` - 87 calls
- `10_online_code_editors.01_codepen_live.main` - 85 calls
- `09_online_drawing.02_picsart_painting.main` - 83 calls
- `01_basics.sql_basics.workflows.main` - 81 calls
- `10_online_code_editors.04_jsfiddle_frontend.main` - 80 calls
- `04_domain_specific.debugging.validation.ShellCommandValidator.get_test_cases` - 79 calls
- `01_basics.shell_fundamentals.feedback_loop.simulate_interactive_session` - 78 calls
- `benchmark_nlp2cmd.generate_html` - 77 calls
- `03_integrations.toon_format.usage_example.main` - 77 calls
- `03_integrations.validation.config_validation.main` - 68 calls
- `03_integrations.web_development.demo_auto.run_demo_with_test` - 61 calls
- `01_basics.sql_basics.advanced.main` - 60 calls
- `03_integrations.pipelines.infrastructure_health.main` - 59 calls
- `benchmark_nlp2cmd.run_benchmark` - 57 calls
- `benchmark_nlp2cmd.generate_command_errors_report` - 55 calls
- `01_basics.docker_basics.file_repair.main` - 54 calls
- `03_integrations.web_development.demo_auto.interactive_mode` - 54 calls
- `_verbose_helper.dump_page_schema` - 53 calls
- `03_integrations.pipelines.log_analysis.main` - 52 calls
- `benchmark_learning.run_learning_benchmark` - 50 calls
- `09_online_drawing.03_adaptive_drawing.generate_shape_points` - 48 calls
- `04_domain_specific.debugging.generator.debug_generator` - 43 calls
- `08_llm_validation.benchmark_validator.run_benchmark` - 43 calls
- `09_online_drawing.01_draw_chat_shapes.main` - 42 calls
- `_dynamic_orchestrator.DynamicOrchestrator.execute_task` - 42 calls
- `10_online_code_editors.05_dynamic_executor.main` - 40 calls
- `04_domain_specific.polish_llm_integration.04_results_ranking.demo.main` - 40 calls
- `06_desktop_automation.08_captcha_solver.run.main` - 40 calls
- `09_online_drawing.01_draw_chat_shapes.draw_on_canvas` - 39 calls
- `06_desktop_automation.07_canvas_drawing.run.main` - 38 calls
- `03_integrations.toon_format.comparison_demo.demonstrate_llm_friendly_format` - 38 calls
- `benchmark_nlp2cmd.build_summary` - 37 calls
- `03_integrations.toon_format.comparison_demo.benchmark_performance` - 37 calls
- `04_domain_specific.polish_llm_integration.example_pdf_search.test_pdf_search_queries` - 36 calls

## System Interactions

How components interact:

```mermaid
graph TD
```

## Reverse Engineering Guidelines

1. **Entry Points**: Start analysis from the entry points listed above
2. **Core Logic**: Focus on classes with many methods
3. **Data Flow**: Follow data transformation functions
4. **Process Flows**: Use the flow diagrams for execution paths
5. **API Surface**: Public API functions reveal the interface

## Context for LLM

Maintain the identified architectural patterns and public API surface when suggesting changes.