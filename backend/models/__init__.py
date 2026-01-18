# models/__init__.py
"""
Models package for YAML Agent Orchestration System.
Provides clean model routing without direct API imports in executor.
"""

from models.router import call_model

__all__ = ['call_model']
