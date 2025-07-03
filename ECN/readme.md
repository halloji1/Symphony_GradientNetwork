# 🌐 Emergent Collaboration Network (ECN-Layer)

This repository implements the decentralized agent framework for the **Emergent Collaboration Network (ECN)**, where LLM-based agents autonomously discover collaborators, solve tasks, and evolve over time using peer-to-peer protocols.

---

## 🚀 Key Features

- **Flexible Agent Roles:**
  - `FIN` (Full Intelligence Node): Full-featured LLM agent capable of task decomposition, planning, and multi-step coordination.
  - `LTN` (Lightweight Tool Node): Provides atomic execution units (e.g., math solvers, translation tools) with minimal compute.
  - `NAP` (Network Access Point): Bridges non-ECN clients (e.g., users, web interfaces) into the ECN via task relay and result return.

- **ISEP Protocol:** Iterative Scope Exploration Protocol enables decentralized task negotiation via beacon broadcasting and response matching.
- **LoRA-based Skill Evolution:** Local gradient updates with LoRA allow agents to evolve based on real-world interactions and self-play.
- **DID Identity System:** Decentralized identity (DID) guarantees self-sovereignty and supports peer-based reputation tracking.
- **No Central Coordination:** Agents operate in a fully decentralized environment with P2P discovery, coordination, and learning.

---

## 🧱 Project Structure

```bash
ecn_llm/
├── agents/        # FIN, LTN, and NAP agent behavior classes (e.g., planning, execution)
├── models/        # LLM loading, LoRA fine-tuning manager, reward model interfaces
├── protocol/      # Definitions for Beacon, Response, TaskContract, and LoRA Patch
├── core/          # Core logic: identity (DID), capability matching, memory, and reputation tracking
├── runtime/       # Entrypoint CLI runner, configuration system, logging framework
├── tools/         # Modular tool wrappers (e.g., MathTool, TranslateTool, SearchTool)
└── tests/         # Unit and integration tests for all major behaviors and data flows
```

---

## ✨ How It Works

### 1. Initialization
- Load quantized base language model (e.g., TinyLLaMA, Mistral-7B)
- Inject a system prompt and register exposed capabilities
- Assign a unique decentralized identity (DID) and join the ECN

### 2. Exploration (ISEP Protocol)
- A FIN agent initiates a `Beacon` to discover collaborators
- Nearby agents evaluate capability match and respond asynchronously

### 3. Execution & Feedback
- Subtasks are converted to `TaskContract` objects
- Selected FINs or LTNs perform atomic operations and return results
- Rewards are assigned locally and used to update LoRA parameters via self-play or reinforcement

### 4. LoRA Patch Sharing (Optional)
- Agents periodically export skill updates as sparse `LoRA Patch` files
- Neighbors receive and selectively merge via SPARTA-style averaging, preserving communication efficiency

---

## 🛠 Quick Start

```bash
# Run an agent
python runtime/main.py --config runtime/config.yaml

# Supported roles: FIN / LTN / NAP
```

---

## 📄 Example Components

- `models/base_loader.py` – Load and quantize pretrained base models
- `models/lora_manager.py` – LoRA training, patching, and sparse export functions
- `protocol/beacon.py` – Task discovery beacon format
- `protocol/task_contract.py` – Standard contract for subtask execution
- `agents/fin_agent.py` – FIN agent logic for task decomposition and coordination
- `core/identity.py` – DID assignment and signature management
- `core/capability.py` – Capability registration and matching engine
- `tools/tool_math.py` – Declarative math execution wrapper
- `tests/test_agent_selfplay.py` – Agent self-play simulation using internal feedback loops

---