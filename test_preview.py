"""
Skrypt szybkiego testu: generuje 15-sekundowy fragment do walidacji syntezy audio,
pozycji dymku z napisami, equalizera i renderowania wizualnego.
"""
import sys, os
from auto_pipeline import run_auto_pipeline

if __name__ == "__main__":
    print("[TEST] Start 15-sekundowego testu podglądu...")
    run_auto_pipeline(
        target_minutes=0.5,
        topic="Sztuka słuchania się w związku",
        dry_run=True,
        preview_seconds=15.0
    )
