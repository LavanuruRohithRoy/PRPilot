# PRPilot System Overview

PRPilot is an AI-powered Pull Request Intelligence Platform designed to streamline code reviews, automate quality checks, and provide actionable design insights directly within the developer workflow.

---

## PRPilot Vision

The vision of PRPilot is to reduce the review burden on developers by establishing an automated, context-aware intelligence layer between developers and version control platforms. It ensures codebase standards are adhered to, bugs and performance bottlenecks are identified prior to merging, and contextual review metrics are readily available.

---

## Core Components

PRPilot consists of four primary components working in harmony:

1. **Frontend (Next.js)**:
   * A developer-focused web interface built on Next.js.
   * Provides dashboards for monitoring repository performance, reviewing code intelligence analysis, tracking metrics, and adjusting agent settings.

2. **Backend (FastAPI)**:
   * A high-performance, asynchronous REST API powered by FastAPI.
   * Manages webhook payloads, handles requests from the frontend, interfaces with databases, and orchestrates tasks for specialized AI agents.

3. **Foundry IQ**:
   * The underlying cognitive service integration, built on Azure AI Foundry capabilities.
   * Powers advanced semantic code checks, system reasoning loops, and prompt evaluations.

4. **GitHub Integration**:
   * Connects to the GitHub API (via webhooks or GitHub App credentials) to monitor repository activities.
   * Automates the delivery of comments, status checks, and suggested review edits directly on Pull Requests.

---

## Future Agent System

The review pipelines are executed by specialized agents living in the agent framework:

* **Security Agent**: Automates code vulnerability detection, identifies dependency risks, and checks for leaked secrets.
* **Performance Agent**: Evaluates algorithm complexity, highlights expensive operations, and suggests optimization paths.
* **Architecture Agent**: Checks incoming code changes against modular structure guidelines, dependency directions, and design conventions.
* **Summary Agent**: Parses code diffs to construct comprehensive, clear, and human-readable summaries of the pull request modifications.
