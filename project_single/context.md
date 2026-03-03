# System Architecture Analysis

## Overview

- **Project**: /home/tom/github/wronai/nlp2cmd
- **Analysis Mode**: static
- **Total Functions**: 2129
- **Total Classes**: 396
- **Modules**: 206
- **Entry Points**: 0

## Architecture by Module

### generation.template_generator
- **Functions**: 100
- **Classes**: 2
- **File**: `template_generator.py`

### web_schema.form_data_loader
- **Functions**: 47
- **Classes**: 1
- **File**: `form_data_loader.py`

### src.nlp2cmd_part1.schemas
- **Functions**: 43
- **Classes**: 2
- **File**: `__init__.py`

### web_schema.site_explorer
- **Functions**: 33
- **Classes**: 3
- **File**: `site_explorer.py`

### core.toon_integration
- **Functions**: 32
- **Classes**: 1
- **File**: `toon_integration.py`

### generation.semantic_matcher_optimized
- **Functions**: 30
- **Classes**: 3
- **File**: `semantic_matcher_optimized.py`

### generation.data_loader
- **Functions**: 28
- **Classes**: 3
- **File**: `data_loader.py`

### automation.action_planner
- **Functions**: 26
- **Classes**: 3
- **File**: `action_planner.py`

### src.nlp2cmd.processing.framework
- **Functions**: 26
- **Classes**: 9
- **File**: `framework.py`

### src.nlp2cmd_part1.validators
- **Functions**: 25
- **Classes**: 8
- **File**: `__init__.py`

### src.nlp2cmd_part1.thermodynamic
- **Functions**: 25
- **Classes**: 10
- **File**: `__init__.py`

### automation.password_store
- **Functions**: 24
- **Classes**: 6
- **File**: `password_store.py`

### generation.evolutionary_cache
- **Functions**: 24
- **Classes**: 3
- **File**: `evolutionary_cache.py`

### automation.mouse_controller
- **Functions**: 23
- **Classes**: 2
- **File**: `mouse_controller.py`

### generation.fuzzy_schema_matcher
- **Functions**: 23
- **Classes**: 4
- **File**: `fuzzy_schema_matcher.py`

### web_schema.browser_config
- **Functions**: 23
- **Classes**: 2
- **File**: `browser_config.py`

### adapters.browser
- **Functions**: 23
- **Classes**: 2
- **File**: `browser.py`

### adapters.kubernetes
- **Functions**: 23
- **Classes**: 3
- **File**: `kubernetes.py`

### core.core_transform
- **Functions**: 22
- **Classes**: 1
- **File**: `core_transform.py`

### llm.router
- **Functions**: 22
- **Classes**: 3
- **File**: `router.py`

## Key Entry Points

Main execution flows into the system:

## Process Flows

Key execution flows identified:

## Key Classes

### generation.template_generator.TemplateGenerator
> Generate DSL commands from templates.

Uses predefined templates filled with extracted entities.
Fal
- **Methods**: 100
- **Key Methods**: generation.template_generator.TemplateGenerator.__init__, generation.template_generator.TemplateGenerator._load_defaults_from_json, generation.template_generator.TemplateGenerator._load_templates_from_json, generation.template_generator.TemplateGenerator._get_default, generation.template_generator.TemplateGenerator.generate, generation.template_generator.TemplateGenerator._find_alternative_template, generation.template_generator.TemplateGenerator._get_intent_aliases, generation.template_generator.TemplateGenerator._prepare_entities, generation.template_generator.TemplateGenerator._prepare_sql_entities, generation.template_generator.TemplateGenerator._prepare_shell_entities

### web_schema.form_data_loader.FormDataLoader
> Loads form field data from multiple sources:
1. .env file (for sensitive data like email, name, phon
- **Methods**: 45
- **Key Methods**: web_schema.form_data_loader.FormDataLoader.__init__, web_schema.form_data_loader.FormDataLoader._dedupe_preserve_order, web_schema.form_data_loader.FormDataLoader.dedupe_selectors, web_schema.form_data_loader.FormDataLoader._parse_domain, web_schema.form_data_loader.FormDataLoader._safe_domain_filename, web_schema.form_data_loader.FormDataLoader._user_sites_dir, web_schema.form_data_loader.FormDataLoader._project_sites_dir, web_schema.form_data_loader.FormDataLoader._site_profile_paths, web_schema.form_data_loader.FormDataLoader.get_site_profile_write_path, web_schema.form_data_loader.FormDataLoader._load_site_profile_payload

### schemas.SchemaRegistry
> Registry for file format schemas with validation and repair capabilities.
- **Methods**: 37
- **Key Methods**: schemas.SchemaRegistry.__init__, schemas.SchemaRegistry._register_builtin_schemas, schemas.SchemaRegistry.register, schemas.SchemaRegistry.get, schemas.SchemaRegistry.has_schema, schemas.SchemaRegistry.list_schemas, schemas.SchemaRegistry.unregister, schemas.SchemaRegistry.find_schema_for_file, schemas.SchemaRegistry.find_schema_by_mime_type, schemas.SchemaRegistry.find_extension_conflicts

### core.toon_integration.ToonDataManager
> Unified data manager using TOON format
- **Methods**: 27
- **Key Methods**: core.toon_integration.ToonDataManager.__init__, core.toon_integration.ToonDataManager._ensure_loaded, core.toon_integration.ToonDataManager.get_all_commands, core.toon_integration.ToonDataManager.get_shell_commands, core.toon_integration.ToonDataManager.get_browser_commands, core.toon_integration.ToonDataManager.get_command_by_name, core.toon_integration.ToonDataManager.search_commands, core.toon_integration.ToonDataManager.get_config, core.toon_integration.ToonDataManager.get_llm_config, core.toon_integration.ToonDataManager.get_test_commands

### web_schema.site_explorer.SiteExplorer
> Explores website to find forms, contact pages, and other content.

Usage:
    explorer = SiteExplore
- **Methods**: 27
- **Key Methods**: web_schema.site_explorer.SiteExplorer.__init__, web_schema.site_explorer.SiteExplorer._setup_resource_blocking, web_schema.site_explorer.SiteExplorer._resolve_platform_url, web_schema.site_explorer.SiteExplorer._goto_with_retry, web_schema.site_explorer.SiteExplorer._try_github_api, web_schema.site_explorer.SiteExplorer._detect_docs_framework, web_schema.site_explorer.SiteExplorer._record_timing, web_schema.site_explorer.SiteExplorer.get_timing_stats, web_schema.site_explorer.SiteExplorer._fallback_static_scrape, web_schema.site_explorer.SiteExplorer.find_content

### core.core_transform.NLP2CMD
> Main class for Natural Language to Command transformation.

This class orchestrates the transformati
- **Methods**: 23
- **Key Methods**: core.core_transform.NLP2CMD.__init__, core.core_transform.NLP2CMD.transform, core.core_transform.NLP2CMD.transform_ir, core.core_transform.NLP2CMD._normalize_entities, core.core_transform.NLP2CMD._normalize_entities_sql, core.core_transform.NLP2CMD._normalize_entities_shell, core.core_transform.NLP2CMD._normalize_entities_docker, core.core_transform.NLP2CMD._normalize_entities_kubernetes, core.core_transform.NLP2CMD._normalize_entities_dql, core.core_transform.NLP2CMD._normalize_shell_entities

### adapters.browser.BrowserAdapter
> Minimal adapter that turns NL into dom_dql.v1 navigation (Playwright).
- **Methods**: 22
- **Key Methods**: adapters.browser.BrowserAdapter.__init__, adapters.browser.BrowserAdapter._extract_url, adapters.browser.BrowserAdapter._extract_type_text, adapters.browser.BrowserAdapter._has_type_action, adapters.browser.BrowserAdapter._should_explore_for_content, adapters.browser.BrowserAdapter._should_explore_for_forms, adapters.browser.BrowserAdapter._has_fill_form_action, adapters.browser.BrowserAdapter._has_press_enter, adapters.browser.BrowserAdapter._has_form_action, adapters.browser.BrowserAdapter._has_submit_action
- **Inherits**: BaseDSLAdapter

### adapters.kubernetes.KubernetesAdapter
> Kubernetes adapter for kubectl commands and manifests.

Transforms natural language into kubectl com
- **Methods**: 22
- **Key Methods**: adapters.kubernetes.KubernetesAdapter.__init__, adapters.kubernetes.KubernetesAdapter._parse_cluster_context, adapters.kubernetes.KubernetesAdapter._normalize_resource, adapters.kubernetes.KubernetesAdapter.generate, adapters.kubernetes.KubernetesAdapter._generate_get, adapters.kubernetes.KubernetesAdapter._generate_describe, adapters.kubernetes.KubernetesAdapter._generate_apply, adapters.kubernetes.KubernetesAdapter._generate_delete, adapters.kubernetes.KubernetesAdapter._generate_scale, adapters.kubernetes.KubernetesAdapter._generate_logs
- **Inherits**: BaseDSLAdapter

### automation.action_planner.ActionPlanner
> Decomposes complex NL commands into ActionPlan via rules or LLM.

Costs:
- Rule match (known service
- **Methods**: 21
- **Key Methods**: automation.action_planner.ActionPlanner.__init__, automation.action_planner.ActionPlanner.decompose, automation.action_planner.ActionPlanner.decompose_sync, automation.action_planner.ActionPlanner._try_rule_decomposition, automation.action_planner.ActionPlanner._resolve_service, automation.action_planner.ActionPlanner._wants_new_tab, automation.action_planner.ActionPlanner._wants_existing_firefox, automation.action_planner.ActionPlanner._wants_create_key, automation.action_planner.ActionPlanner._build_navigation_steps, automation.action_planner.ActionPlanner._build_session_check_steps

### generation.evolutionary_cache.EvolutionaryCache
> Manages the .nlp2cmd/ learned schema cache.

Usage:
    cache = EvolutionaryCache()
    result = cac
- **Methods**: 20
- **Key Methods**: generation.evolutionary_cache.EvolutionaryCache.__init__, generation.evolutionary_cache.EvolutionaryCache._ensure_dir, generation.evolutionary_cache.EvolutionaryCache._load, generation.evolutionary_cache.EvolutionaryCache.save, generation.evolutionary_cache.EvolutionaryCache.lookup, generation.evolutionary_cache.EvolutionaryCache._ask_teacher, generation.evolutionary_cache.EvolutionaryCache._clean, generation.evolutionary_cache.EvolutionaryCache._try_template_pipeline, generation.evolutionary_cache.EvolutionaryCache._try_english_pipeline, generation.evolutionary_cache.EvolutionaryCache._try_polish_template

### generation.semantic_matcher_optimized.OptimizedSemanticMatcher
> Optimized semantic similarity matcher using sentence embeddings.

Features:
- Handles typos and para
- **Methods**: 20
- **Key Methods**: generation.semantic_matcher_optimized.OptimizedSemanticMatcher.__init__, generation.semantic_matcher_optimized.OptimizedSemanticMatcher._preload_models, generation.semantic_matcher_optimized.OptimizedSemanticMatcher._get_model, generation.semantic_matcher_optimized.OptimizedSemanticMatcher._get_polish_model, generation.semantic_matcher_optimized.OptimizedSemanticMatcher._load_model, generation.semantic_matcher_optimized.OptimizedSemanticMatcher.add_intent, generation.semantic_matcher_optimized.OptimizedSemanticMatcher.add_intents_batch, generation.semantic_matcher_optimized.OptimizedSemanticMatcher._encode_text, generation.semantic_matcher_optimized.OptimizedSemanticMatcher._encode_batch, generation.semantic_matcher_optimized.OptimizedSemanticMatcher._encode_with_cache

### parsing.toon_parser.ToonParser
> Unified TOON format parser with hierarchical access
- **Methods**: 20
- **Key Methods**: parsing.toon_parser.ToonParser.__init__, parsing.toon_parser.ToonParser.parse_file, parsing.toon_parser.ToonParser.parse_content, parsing.toon_parser.ToonParser._parse_lines, parsing.toon_parser.ToonParser._parse_array_node, parsing.toon_parser.ToonParser._parse_object_node, parsing.toon_parser.ToonParser._parse_key_value, parsing.toon_parser.ToonParser._parse_value, parsing.toon_parser.ToonParser._extract_categories, parsing.toon_parser.ToonParser.get_category

### automation.step_validator.StepValidator
> Validates pre/post conditions for ActionPlan steps.

Checks clipboard state, DOM elements, environme
- **Methods**: 19
- **Key Methods**: automation.step_validator.StepValidator.__init__, automation.step_validator.StepValidator.metrics, automation.step_validator.StepValidator.start_step, automation.step_validator.StepValidator.finish_step, automation.step_validator.StepValidator.get_clipboard, automation.step_validator.StepValidator.set_clipboard, automation.step_validator.StepValidator.snapshot_clipboard, automation.step_validator.StepValidator.clipboard_changed, automation.step_validator.StepValidator.validate_pre_navigate, automation.step_validator.StepValidator.validate_pre_check_session

### automation.mouse_controller.MouseController
> Advanced mouse control via Playwright with human-like movements.

Supports:
- Click, double-click, r
- **Methods**: 19
- **Key Methods**: automation.mouse_controller.MouseController.__init__, automation.mouse_controller.MouseController._jitter, automation.mouse_controller.MouseController._human_delay, automation.mouse_controller.MouseController.click, automation.mouse_controller.MouseController.double_click, automation.mouse_controller.MouseController.right_click, automation.mouse_controller.MouseController.move_to, automation.mouse_controller.MouseController.drag, automation.mouse_controller.MouseController._compute_bezier, automation.mouse_controller.MouseController.bezier_move

### generation.fuzzy_schema_matcher.FuzzySchemaMatcher
> Language-agnostic fuzzy matcher using JSON schemas.

Works with any language by using character-leve
- **Methods**: 19
- **Key Methods**: generation.fuzzy_schema_matcher.FuzzySchemaMatcher.__init__, generation.fuzzy_schema_matcher.FuzzySchemaMatcher.load_schema, generation.fuzzy_schema_matcher.FuzzySchemaMatcher.add_phrase, generation.fuzzy_schema_matcher.FuzzySchemaMatcher.add_phrases_from_dict, generation.fuzzy_schema_matcher.FuzzySchemaMatcher._build_index, generation.fuzzy_schema_matcher.FuzzySchemaMatcher._index_phrase, generation.fuzzy_schema_matcher.FuzzySchemaMatcher._normalize, generation.fuzzy_schema_matcher.FuzzySchemaMatcher._remove_spaces, generation.fuzzy_schema_matcher.FuzzySchemaMatcher._get_ngrams, generation.fuzzy_schema_matcher.FuzzySchemaMatcher._ngram_similarity

### adapters.dynamic.DynamicAdapter
> Dynamic adapter that uses extracted schemas instead of hardcoded patterns.

This adapter can work wi
- **Methods**: 19
- **Key Methods**: adapters.dynamic.DynamicAdapter.__init__, adapters.dynamic.DynamicAdapter.check_safety, adapters.dynamic.DynamicAdapter._load_common_commands, adapters.dynamic.DynamicAdapter.register_schema_source, adapters.dynamic.DynamicAdapter.generate, adapters.dynamic.DynamicAdapter._find_matching_commands, adapters.dynamic.DynamicAdapter._generate_from_schema, adapters.dynamic.DynamicAdapter._generate_make_command, adapters.dynamic.DynamicAdapter._generate_web_dql, adapters.dynamic.DynamicAdapter._generate_from_template
- **Inherits**: BaseDSLAdapter

### adapters.desktop.DesktopAdapter
> Adapter for desktop GUI automation via VNC/noVNC + xdotool/wmctrl.
- **Methods**: 19
- **Key Methods**: adapters.desktop.DesktopAdapter.__init__, adapters.desktop.DesktopAdapter.generate, adapters.desktop.DesktopAdapter._build_actions, adapters.desktop.DesktopAdapter._build_email_actions, adapters.desktop.DesktopAdapter._build_email_compose, adapters.desktop.DesktopAdapter._detect_followup_actions, adapters.desktop.DesktopAdapter.detect_intent, adapters.desktop.DesktopAdapter._extract_app_name, adapters.desktop.DesktopAdapter._extract_quoted_text, adapters.desktop.DesktopAdapter._extract_shortcut
- **Inherits**: BaseAdapter

### generation.pipeline.RuleBasedPipeline
> Complete rule-based NL → DSL pipeline.

Combines intent detection, entity extraction, and template g
- **Methods**: 18
- **Key Methods**: generation.pipeline.RuleBasedPipeline.__init__, generation.pipeline.RuleBasedPipeline.complex_detector, generation.pipeline.RuleBasedPipeline.action_planner, generation.pipeline.RuleBasedPipeline.evolutionary_cache, generation.pipeline.RuleBasedPipeline.enhanced_detector, generation.pipeline.RuleBasedPipeline.process, generation.pipeline.RuleBasedPipeline.process_steps, generation.pipeline.RuleBasedPipeline._process_with_detection, generation.pipeline.RuleBasedPipeline._split_sentences, generation.pipeline.RuleBasedPipeline._persist_result

### web_schema.browser_config.BrowserConfigLoader
> Single source of truth for browser automation config.

Loads from ``data/browser_config/*.yaml`` wit
- **Methods**: 18
- **Key Methods**: web_schema.browser_config.BrowserConfigLoader.__init__, web_schema.browser_config.BrowserConfigLoader._ensure_loaded, web_schema.browser_config.BrowserConfigLoader.get_dismiss_selectors, web_schema.browser_config.BrowserConfigLoader.get_submit_selectors, web_schema.browser_config.BrowserConfigLoader.get_type_selectors, web_schema.browser_config.BrowserConfigLoader.get_contact_page_link_selectors, web_schema.browser_config.BrowserConfigLoader.get_common_contact_paths, web_schema.browser_config.BrowserConfigLoader.get_contact_url_keywords, web_schema.browser_config.BrowserConfigLoader.get_contact_page_keywords, web_schema.browser_config.BrowserConfigLoader.get_junk_field_types

### adapters.docker.DockerAdapter
> Docker adapter for CLI and Compose operations.

Transforms natural language into Docker commands
wit
- **Methods**: 18
- **Key Methods**: adapters.docker.DockerAdapter.__init__, adapters.docker.DockerAdapter._parse_compose_context, adapters.docker.DockerAdapter.generate, adapters.docker.DockerAdapter._generate_run, adapters.docker.DockerAdapter._generate_stop, adapters.docker.DockerAdapter._generate_remove, adapters.docker.DockerAdapter._generate_build, adapters.docker.DockerAdapter._generate_pull, adapters.docker.DockerAdapter._generate_compose_up, adapters.docker.DockerAdapter._generate_compose_down
- **Inherits**: BaseDSLAdapter

## Data Transformation Functions

Key functions that process and transform data:

### pipeline_runner_shell.ShellExecutionMixin._parse_shell_command
- **Output to**: command.strip, cmd.lower, any, any, re.search

### schema_driven.SchemaDrivenNLP2CMD.transform
- **Output to**: self._select_action, self._extract_params, self._render_dsl, str, ActionIR

### monitoring.token_costs.TokenCostEstimator.format_estimate
> Format token cost estimate for display.
- **Output to**: None.join, lines.append

### monitoring.token_costs.format_token_estimate
> Format token cost estimate for display.
- **Output to**: _estimator.format_estimate

### monitoring.token_costs.parse_metrics_string
> Parse metrics string like '⏱️ Time: 2.6ms | 💻 CPU: 0.0% | 🧠 RAM: 53.5MB (0.1%) | ⚡ Energy: 0.022mJ'
- **Output to**: None.strip, None.strip, None.strip, None.strip, float

### automation.action_planner.ActionPlanner._parse_llm_response
> Parse LLM JSON response into ActionPlan.
- **Output to**: re.sub, re.sub, ActionPlan, raw.strip, json.loads

### automation.schema_fallback.SchemaFallback._parse_llm_steps
> Parse LLM response into step dictionaries.
- **Output to**: isinstance, json.loads, isinstance, s.get, s.get

### monitoring.resources.ResourceMonitor._process_cpu_time_seconds
> Return process CPU time in seconds (user+system).
- **Output to**: self.process.cpu_times, float, float, getattr, getattr

### monitoring.resources.ResourceMonitor.format_metrics
> Format metrics for display.
- **Output to**: None.join, lines.append

### monitoring.resources.format_last_metrics
> Format metrics from last execution for display.
- **Output to**: monitoring.resources.get_last_metrics, _monitor.format_metrics

### automation.step_validator.StepValidator.validate_pre_navigate
> Validate before navigation step.
- **Output to**: params.get, ValidationResult, ValidationResult, url.startswith, ValidationResult

### automation.step_validator.StepValidator.validate_pre_check_session
> Validate before session check — page must be loaded.
- **Output to**: ValidationResult, ValidationResult, ValidationResult

### automation.step_validator.StepValidator.validate_pre_extract_key
> Validate before key extraction — must be on correct page.
- **Output to**: self.snapshot_clipboard, ValidationResult, ValidationResult, params.get, ValidationResult

### automation.step_validator.StepValidator.validate_pre_prompt_secret
> Validate before prompting for secret — check if already available.
- **Output to**: params.get, None.strip, os.environ.get, variables.items, ValidationResult

### automation.step_validator.StepValidator.validate_post_navigate
> Validate after navigation — page loaded?
- **Output to**: ValidationResult, params.get, page.title, ValidationResult, ValidationResult

### automation.step_validator.StepValidator.validate_post_check_session
> Validate after session check — is user logged in?
- **Output to**: ValidationResult, ValidationResult, params.get, ValidationResult

### automation.step_validator.StepValidator.validate_post_extract_key
> Validate after key extraction — did we get a valid key?
- **Output to**: params.get, self.clipboard_changed, ValidationResult, ValidationResult, re.match

### automation.step_validator.StepValidator.validate_post_save_env
> Validate after saving to .env — does file contain the variable?
- **Output to**: params.get, params.get, ValidationResult, ValidationResult, open

### automation.step_validator.StepValidator.validate_pre
> Dispatch pre-condition validation based on action type.
- **Output to**: validators.get, ValidationResult, validator, self.validate_pre_navigate, self.validate_pre_check_session

### automation.step_validator.StepValidator.validate_post
> Dispatch post-condition validation based on action type.
- **Output to**: validators.get, ValidationResult, validator, self.validate_post_navigate, self.validate_post_check_session

### schemas.FileFormatSchema.validate
> Validate content using this schema.
- **Output to**: self.validator

### schemas.FileFormatSchema.parse
> Parse content using this schema.
- **Output to**: self.parser

### schemas.FileFormatSchema.self_validate
> Validate the schema itself.
- **Output to**: errors.append, errors.append, errors.append, errors.append, errors.append

### schemas.SchemaRegistry.validate_integrity
> Validate registry integrity.
- **Output to**: self._schemas.items, self.find_extension_conflicts, isinstance, ValueError

### schemas.SchemaRegistry.detect_format
> Detect file format from path.
- **Output to**: str, self._schemas.values, self._detect_by_content, max, self._match_pattern

## Public API Surface

Functions exposed as public API (no underscore prefix):

- `pipeline_runner_plans.PlanExecutionMixin.execute_action_plan` - 261 calls
- `cli.commands.run.handle_run_mode` - 261 calls
- `adapters.canvas.CanvasAdapter.execute_drawing_plan` - 193 calls
- `cli.main.main` - 115 calls
- `execution.runner.ExecutionRunner.run_command` - 109 calls
- `generation.train_model.train_all_models` - 86 calls
- `web_schema.form_handler.FormHandler.detect_form_fields` - 83 calls
- `web_schema.site_explorer.SiteExplorer.find_form` - 77 calls
- `adapters.browser.BrowserAdapter.generate` - 66 calls
- `cli.commands.generate.handle_generate_query` - 66 calls
- `web_schema.site_explorer.SiteExplorer.find_content` - 60 calls
- `generation.evolutionary_cache.EvolutionaryCache.lookup` - 57 calls
- `cli.debug_info.show_schema_info` - 57 calls
- `cli.debug_info.show_decision_tree_info` - 56 calls
- `validators.DockerValidator.validate` - 52 calls
- `feedback.FeedbackAnalyzer.analyze` - 51 calls
- `schema_extraction.script_extractors.ShellScriptExtractor.extract_from_source` - 51 calls
- `storage.versioned_store.demonstrate_version_management` - 50 calls
- `execution.runner.ExecutionRunner.run_with_recovery` - 50 calls
- `service.cli.add_service_command` - 45 calls
- `generation.pipeline.RuleBasedPipeline.process` - 43 calls
- `validators.KubernetesValidator.validate` - 43 calls
- `schema_extraction.script_extractors.MakefileExtractor.extract_from_source` - 41 calls
- `cli.history.show_stats` - 39 calls
- `generation.thermodynamic.ThermodynamicGenerator.generate` - 38 calls
- `web_schema.form_handler.FormHandler.fill_form` - 35 calls
- `adapters.shell_generators.FileOperationGenerator.generate_file_search` - 34 calls
- `cli.commands.interactive.InteractiveSession.display_feedback` - 34 calls
- `utils.external_cache.main` - 33 calls
- `schema_extraction.llm_extractor.LLMSchemaExtractor.extract_from_command` - 33 calls
- `cli.web_schema.extract_schema` - 32 calls
- `validators.SQLValidator.validate` - 31 calls
- `storage.per_command_store.test_per_command_store` - 30 calls
- `generation.evolutionary_cache.EvolutionaryCache.lookup_multistep` - 29 calls
- `web_schema.form_handler.FormHandler.automatic_fill` - 29 calls
- `thermodynamic.energy_models.AllocationEnergy.energy` - 29 calls
- `generation.thermodynamic.ThermodynamicGenerator.validate_solution` - 28 calls
- `validators.ShellValidator.validate` - 28 calls
- `cli.web_schema.show_history` - 28 calls
- `adapters.dynamic.DynamicAdapter.register_schema_source` - 28 calls

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