# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI - Codebase Digest & Durability Audit Generator
# Created & Patented by Chinmay Hudedamani.

import os
import sys
import io
from pathlib import Path

# Force UTF-8 stdout encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SOURCE_FILES = [
    "core/engine.py",
    "clinical/rag_generator.py",
    "core/rl_bandit_policy.py",
    "core/intent_classifier.py",
    "core/doctor_assistant.py",
    "clinical/ledger_writer.py",
    "core/security_shield.py",
    "core/rate_limiter.py",
    "core/conversation_store.py",
    "rl_benchmark_evaluator.py",
    "run_all_tests.py",
    "app.py",
    "setup_db.py",
    "schema.sql",
    "clinical/clinic_knowledge_base.json"
]

OUTPUT_FILE = Path("CODEBASE_DURABILITY_AUDIT_DIGEST.md")

def build_codebase_digest():
    print("📦 Bundling APEX AI Codebase into Audit Digest...")
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        out.write("# APEX AI — DENTAL CLINIC WHATSAPP ASSISTANT\n")
        out.write("### Complete Proprietary Codebase & Durability Audit Digest\n")
        out.write("**Created & Patented by:** Chinmay Hudedamani\n")
        out.write("**Architecture:** RL Contextual Bandit + Zero-Hallucination RAG + Neon Serverless PostgreSQL\n\n")
        out.write("---\n\n")
        
        for rel_path in SOURCE_FILES:
            file_path = Path(rel_path)
            if file_path.exists():
                out.write(f"## 📄 File: `{rel_path}`\n\n")
                out.write("```" + ("python" if rel_path.endswith(".py") else ("json" if rel_path.endswith(".json") else "sql")) + "\n")
                with open(file_path, "r", encoding="utf-8") as f:
                    out.write(f.read())
                out.write("\n```\n\n---\n\n")
            else:
                print(f"⚠️ Warning: File {rel_path} not found.")
                
    print(f"✅ Codebase Audit Digest created successfully at: {OUTPUT_FILE.resolve()}")

if __name__ == "__main__":
    build_codebase_digest()
