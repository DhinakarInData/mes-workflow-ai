# MES Workflow AI

An AI-assisted workflow automation platform that converts natural language manufacturing process descriptions into structured MES/FDS-style workflow diagrams.

The system combines **Generative AI** with a **deterministic workflow compiler** to produce clean, reviewable, and editable workflow diagrams suitable for Manufacturing Execution System (MES) documentation.

---

# Why This Project?

Creating Functional Design Specification (FDS) workflow diagrams is a time-consuming manual activity.

Typically, MES engineers create workflows in tools such as Microsoft Visio by manually interpreting:

- Standard Operating Procedures (SOPs)
- Manufacturing process descriptions
- Batch Manufacturing Records (BMR)
- User Requirement Specifications (URS)
- Business process discussions
- Validation documents

This process requires both domain expertise and significant manual effort.

MES Workflow AI automates this process by transforming natural language process descriptions into structured workflow diagrams while preserving MES/FDS design principles.

---

# Project Vision

Allow users to describe manufacturing workflows in plain English (or voice), and automatically generate:

- MES/FDS-style workflow diagrams
- Reviewable process flows
- Structured workflow graphs
- Future Visio-compatible exports

Example:

```
Scan Equipment

If equipment is invalid,
display an error message
and return to Scan Equipment.

If valid,
continue to Line Clearance.

If Line Clearance is complete,
allow the operator to proceed.
```

↓

Automatically generates a structured workflow diagram.

---

# Key Features

- Natural Language Workflow Extraction
- AI-assisted Workflow Generation
- Deterministic Workflow Compiler
- Graph-based Workflow Engine
- Automatic Routing Engine
- Topology Layout Engine
- ReactFlow Diagram Generation
- MES/FDS Node Library
- Orthogonal Edge Routing
- Error Branch Routing
- Retry Loop Handling
- Restart Flow Separation
- Merge Handling
- Visual Validation Engine
- Layout Stability Checks

---

# Architecture

```
Natural Language Input
            │
            ▼
    Generative AI (LLM)
            │
            ▼
 Structured Workflow JSON
            │
            ▼
 Intermediate Representation (IR)
            │
            ▼
      Graph Generation
            │
            ▼
 Merge & Routing Engine
            │
            ▼
 Topology Layout Engine
            │
            ▼
 ReactFlow Adapter
            │
            ▼
 React Frontend Rendering
            │
            ▼
 FDS Visual Validation
```

---

# AI + Deterministic Engineering

The project intentionally separates AI from diagram generation.

## Generative AI

Responsible for:

- Understanding natural language
- Extracting workflow steps
- Identifying decisions
- Detecting responses
- Generating structured workflow JSON

## Deterministic Compiler

Responsible for:

- Workflow parsing
- Graph construction
- Routing classification
- Node placement
- Topology layout
- Diagram rendering
- Visual validation

This architecture ensures layout quality does not depend entirely on LLM output.

---

# Supported Workflow Components

## Nodes

- Start
- End
- Manual Activity
- System Activity
- System Check
- User Response
- System Response
- QA Response
- Supervisor Response

## Flow Types

- Main Flow
- Success Flow
- Error Flow
- Retry Loop
- Restart Flow
- Review/Rework Flow
- Terminal Flow

---

# FDS Rendering Principles

The rendering engine is designed around real Manufacturing Execution System workflow standards.

It focuses on:

- Stable workflow spine
- Clean orthogonal routing
- Readable error branches
- Retry loop separation
- Restart flow isolation
- Label clarity
- Minimal edge crossings
- Collision-free layout
- FDS-style visual appearance

---

# Visual Validation Engine

Instead of rendering diagrams directly, every generated workflow passes through a validation layer.

Current validations include:

- Node overlap detection
- Edge crossing detection
- Lane overlap detection
- Routing validation
- Target-side congestion detection
- Label placement validation
- FDS layout rule validation

This forms the foundation for future automatic layout correction.

---

# Technology Stack

### Backend

- Python
- FastAPI

### Frontend

- ReactJS
- ReactFlow

### AI

- Google Gemini
- Prompt Engineering
- Context Engineering

### Workflow Engine

- Graph Compiler
- Routing Engine
- Topology Layout Engine
- ReactFlow Adapter
- FDS Visual Validator

---

# Current Status

### Implemented

- AI workflow extraction
- Workflow compiler
- Graph generation
- Routing engine
- Topology layout
- ReactFlow rendering
- Custom nodes
- Orthogonal edge routing
- Error branches
- Retry loops
- Restart flows
- FDS visual validation

### In Progress

- Automatic collision correction
- Intelligent lane optimization
- Dynamic spacing engine
- Connector support
- Pagination
- Visio export

---

# Future Roadmap

### Phase 1

- Stable FDS Layout

### Phase 2

- Automatic Layout Correction
- Collision Resolution
- Smart Lane Selection

### Phase 3

- Multi-page Workflow Support
- Connectors
- A4 Layout

### Phase 4

- Microsoft Visio Export
- FDS Document Generation
- Workflow Table Generation

---

# Long-Term Vision

Create an intelligent workflow engineering platform where users simply describe a manufacturing process in natural language, and the system automatically generates clean, reviewable, and editable MES/FDS workflow documentation.

The goal is not simply to draw diagrams—it is to automate workflow engineering for Manufacturing Execution Systems using a combination of Generative AI and deterministic compiler techniques.
