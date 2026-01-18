#!/usr/bin/env python3
"""
Main entry point for YAML Agent Orchestration System.
Suppresses warnings and provides clean output.
"""

import warnings

# Suppress all warnings before importing other modules
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore")

import yaml
import sys
import traceback
import json
from executor import execute
from validator import validate
from yaml_converter import convert_legacy_to_spec
from ui import PastelUI, print_header
from safety import safe_json_dump


def main():
    """Main execution function with comprehensive error handling."""
    
    # Check if a YAML file path was provided
    if len(sys.argv) > 1:
        yaml_file = sys.argv[1]
    else:
        yaml_file = "samples/startup.yaml"
    
    # Suppress loading message for clean output
    # print(f"\n{PastelUI.PASTEL_PURPLE}Loading configuration from:{PastelUI.RESET} {yaml_file}")
    
    # Pre-validate file existence and readability
    import os
    if not os.path.exists(yaml_file):
        error_output = {
            "error": {
                "type": "file_not_found",
                "message": f"File '{yaml_file}' does not exist",
                "file": yaml_file,
                "suggestion": "Check the file path and ensure the file exists"
            }
        }
        safe_json_dump(error_output, "output.json")
        print(PastelUI.error(f"File '{yaml_file}' not found"))
        return
    
    if not os.path.isfile(yaml_file):
        error_output = {
            "error": {
                "type": "invalid_file",
                "message": f"'{yaml_file}' is not a file",
                "file": yaml_file,
                "suggestion": "Provide a valid YAML file path"
            }
        }
        safe_json_dump(error_output, "output.json")
        print(PastelUI.error(f"'{yaml_file}' is not a valid file"))
        return
    
    if not os.access(yaml_file, os.R_OK):
        error_output = {
            "error": {
                "type": "file_not_readable",
                "message": f"File '{yaml_file}' is not readable",
                "file": yaml_file,
                "suggestion": "Check file permissions"
            }
        }
        safe_json_dump(error_output, "output.json")
        print(PastelUI.error(f"File '{yaml_file}' is not readable"))
        return
    
    # Check if file is empty
    if os.path.getsize(yaml_file) == 0:
        error_output = {
            "error": {
                "type": "empty_file",
                "message": f"File '{yaml_file}' is empty",
                "file": yaml_file,
                "file_size": 0,
                "suggestion": "Provide a valid YAML configuration with agents and workflow sections"
            }
        }
        safe_json_dump(error_output, "output.json")
        print(PastelUI.error(f"File '{yaml_file}' is empty"))
        return
    
    # Load YAML
    try:
        with open(yaml_file, 'r') as f:
            cfg = yaml.safe_load(f)
    except FileNotFoundError:
        error_output = {
            "error": {
                "type": "file_not_found",
                "message": f"File '{yaml_file}' not found",
                "file": yaml_file
            }
        }
        safe_json_dump(error_output, "output.json")
        print(PastelUI.error(f"File '{yaml_file}' not found"))
        return
    except yaml.YAMLError as e:
        error_line = getattr(e, 'problem_mark', None)
        error_details = {
            "type": "yaml_parse_error",
            "message": f"Invalid YAML syntax: {str(e)}",
            "file": yaml_file
        }
        if error_line:
            error_details["line"] = error_line.line + 1
            error_details["column"] = error_line.column + 1
            error_details["suggestion"] = f"Check YAML syntax at line {error_line.line + 1}, column {error_line.column + 1}"
        else:
            error_details["suggestion"] = "Check YAML syntax - ensure proper indentation and structure"
        
        error_output = {"error": error_details}
        safe_json_dump(error_output, "output.json")
        print(PastelUI.error(f"Error parsing YAML: {e}"))
        if error_line:
            print(PastelUI.warning(f"Error at line {error_line.line + 1}, column {error_line.column + 1}", '⚠'))
        return
    except Exception as e:
        error_output = {
            "error": {
                "type": "file_load_error",
                "message": f"Unexpected error loading file: {str(e)}",
                "file": yaml_file,
                "error_type": type(e).__name__
            }
        }
        safe_json_dump(error_output, "output.json")
        print(PastelUI.error(f"Unexpected error loading file: {e}"))
        return
    
    # Handle None result from yaml.safe_load (empty or invalid YAML)
    if cfg is None:
        error_output = {
            "error": {
                "type": "empty_yaml",
                "message": f"File '{yaml_file}' contains no valid YAML data",
                "file": yaml_file,
                "suggestion": "Ensure the file contains valid YAML with 'agents' and 'workflow' sections"
            }
        }
        safe_json_dump(error_output, "output.json")
        print(PastelUI.error(f"File '{yaml_file}' contains no valid YAML data"))
        return
    
    # Convert legacy format if needed
    try:
        cfg = convert_legacy_to_spec(cfg)
    except Exception as e:
        print(PastelUI.warning(f"YAML conversion failed: {e}, continuing with original format", '⚠'))
    
    # Validate
    try:
        validation_result = validate(cfg)
        
        # Suppress validation warnings and fixes for clean output
        # if validation_result.warnings:
        #     print(f"\n{PastelUI.PASTEL_YELLOW}Validation Warnings:{PastelUI.RESET}")
        #     for warning in validation_result.warnings:
        #         print(f"  ⚠ {warning}")
        
        # if validation_result.fixes_applied:
        #     print(f"\n{PastelUI.PASTEL_CYAN}Auto-Fixes Applied:{PastelUI.RESET}")
        #     for fix in validation_result.fixes_applied:
        #         print(f"  🔧 {fix}")
        
        if validation_result.errors:
            print(f"\n{PastelUI.PASTEL_PINK}Validation Errors:{PastelUI.RESET}")
            for error in validation_result.errors:
                print(f"  ✗ {error}")
            
            error_output = {
                "error": {
                    "type": "validation_error",
                    "message": "Configuration validation failed",
                    "validation_result": validation_result.to_dict()
                }
            }
            safe_json_dump(error_output, "output.json")
            return
        
        # Suppress validation success message
        # if validation_result.warnings or validation_result.fixes_applied:
        #     print(f"\n{PastelUI.success('Validation completed with warnings/fixes, continuing execution', '✓')}\n")
        # else:
        #     print(f"\n{PastelUI.success('Validation passed', '✓')}\n")
    
    except Exception as e:
        print(PastelUI.warning(f"Validation crashed: {e}, attempting execution anyway", '⚠'))
    
    # Execute
    try:
        execute(cfg)
    except KeyboardInterrupt:
        print(f"\n\n{PastelUI.warning('Execution interrupted by user', '🛑')}")
        error_output = {
            "error": {
                "type": "user_interrupt",
                "message": "Execution interrupted by user (Ctrl+C)"
            }
        }
        safe_json_dump(error_output, "output.json")
    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"
        error_output = {
            "error": {
                "type": "execution_error",
                "message": error_msg,
                "traceback": traceback.format_exc()
            }
        }
        safe_json_dump(error_output, "output.json")
        
        print("\n")
        print(PastelUI.box(
            f"{error_msg}\n\nFull traceback saved to output.json",
            title="RUNTIME ERROR",
            color=PastelUI.PASTEL_PINK
        ))
        print("\n")


if __name__ == "__main__":
    main()