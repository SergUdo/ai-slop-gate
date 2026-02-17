Quick Start Guide
=================

This guide will help you get started with ai-slop-gate in minutes.

Installation
------------

**1. Clone the repository:**

.. code-block:: bash

   git clone https://github.com/SergUdo/ai-slop-gate.git
   cd ai-slop-gate

**2. Set up Python environment:**

.. code-block:: bash

   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -e .

**3. Initialize configuration:**

.. code-block:: bash

   python -m ai_slop_gate.cli init

This creates ``.ai-slop-gate.yml`` with default settings.

Environment Variables
---------------------

Create a ``.env`` file in the project root:

.. code-block:: bash

   # Required for GitHub PR commenting
   GITHUB_TOKEN=your_github_personal_access_token

   # Provider Keys (add based on your configuration)
   GEMINI_API_KEY=your_google_gemini_api_key
   GROQ_API_KEY=your_groq_api_key
   GITLAB_TOKEN=your_gitlab_token  # For GitLab integration

Your First Analysis
-------------------

**Static Analysis (Fast, No API Keys Required)**

.. code-block:: bash

   python -m ai_slop_gate.cli run --provider static --policy policy.yml

This performs:

- Secret detection (hardcoded API keys, passwords)
- Dangerous function detection (``eval``, ``exec``)
- Dockerfile security checks
- PII detection
- TODO/FIXME tracking
- Supply chain validation

**LLM Analysis (Requires API Key)**

.. code-block:: bash

   python -m ai_slop_gate.cli run --provider gemini --llm-local --policy policy.yml

This performs AI-powered analysis:

- AI slop detection (repetitive, low-quality code)
- Hallucination detection
- Code quality assessment
- Architecture anti-patterns
- **Automatically caches responses** (saves ~67% of tokens!)

**Compliance Check**

.. code-block:: bash

   python -m ai_slop_gate.cli run --compliance --policy policy.yml

This checks:

- GDPR/DSGVO data residency
- License compliance (GPL, AGPL detection)
- Supply chain security
- AI hallucination protection

Using Docker
------------

**Pull the image:**

.. code-block:: bash

   docker pull ghcr.io/sergudo/ai-slop-gate:latest

**Run analysis:**

.. code-block:: bash

   docker run --rm -v $(pwd):/src \
     ghcr.io/sergudo/ai-slop-gate:latest \
     run --provider static --policy /src/policy.yml --path /src

See :doc:`DOCKER` for complete Docker documentation.

Test on Demo Repository
------------------------

Try ai-slop-gate on our demo repository with intentional violations:

.. code-block:: bash

   git clone https://github.com/SergUdo/slop_test
   python -m ai_slop_gate.cli run --provider gemini --llm-local --path slop_test

This repository contains:

- Hardcoded secrets
- AI-generated slop
- License violations
- Security issues

**Live Example:** Check `this PR <https://github.com/SergUdo/slop_test/pull/7>`_ where ai-slop-gate automatically analyzed violations.

Supported Providers
-------------------

.. list-table::
   :header-rows: 1
   :widths: 20 20 15 45

   * - Provider
     - Type
     - Cache
     - Description
   * - ``static``
     - Static Analysis
     - ❌ No
     - Fast static analysis (secrets, eval, Dockerfile, PII)
   * - ``gemini``
     - LLM
     - ✅ Yes
     - Google Gemini (local or GitHub PR)
   * - ``groq``
     - LLM
     - ✅ Yes
     - Groq (Llama 3.3)
   * - ``ollama``
     - LLM
     - ✅ Yes
     - Local Ollama models (100% private)
   * - ``compliance``
     - Compliance
     - ❌ No
     - GDPR, EU residency, license checks

Common Use Cases
----------------

**1. Local Development (Before Commit)**

.. code-block:: bash

   # Quick check
   python -m ai_slop_gate.cli run --provider static
   
   # Deep analysis (with cache)
   python -m ai_slop_gate.cli run --provider static gemini --llm-local

**2. Pull Request Analysis**

.. code-block:: bash

   export GITHUB_TOKEN="ghp-xxxxxxxxxxxx"
   export GEMINI_API_KEY="your-key"
   
   python -m ai_slop_gate.cli run \
     --provider gemini \
     --github-repo owner/repo \
     --pr-id 123

**3. CI/CD Pipeline**

.. code-block:: yaml

   # GitHub Actions example
   - name: AI Slop Gate
     run: |
       docker run --rm -v $(pwd):/src \
         -e GEMINI_API_KEY=${{ secrets.GEMINI_API_KEY }} \
         ghcr.io/sergudo/ai-slop-gate:latest \
         run --provider gemini --llm-local --path /src

See :doc:`INTEGRATIONS` for complete CI/CD setup.

**4. Local LLM (100% Private)**

.. code-block:: bash

   # Start Ollama
   docker-compose up -d
   
   # Run analysis (code never leaves your machine)
   python -m ai_slop_gate.cli run --provider ollama --llm-local

Next Steps
----------

- **CLI Reference:** See :doc:`CLI_REFERENCE` for all command-line options
- **Cache Guide:** Learn how to optimize token usage in :doc:`CACHE`
- **Docker Guide:** Full Docker documentation in :doc:`DOCKER`
- **CI/CD Integration:** Set up in GitHub/GitLab with :doc:`INTEGRATIONS`
- **Testing:** Write tests with :doc:`TESTING`
- **Architecture:** Understand the internals in :doc:`ARCHITECTURE`

Troubleshooting
---------------

**"Provider skipped: insufficient context"**

Missing API key. Set environment variable:

.. code-block:: bash

   export GEMINI_API_KEY="your-key"

**"Cache not working"**

Check verbose output:

.. code-block:: bash

   python -m ai_slop_gate.cli run --provider gemini --llm-local --verbose

See cache directory:

.. code-block:: bash

   ls -la .ai-slop-cache/

**"Permission denied"**

Fix permissions:

.. code-block:: bash

   chmod -R u+rw .ai-slop-cache/

For more help, see:

- `GitHub Issues <https://github.com/SergUdo/ai-slop-gate/issues>`_
- `Discussions <https://github.com/SergUdo/ai-slop-gate/discussions>`_
- `Full Documentation <https://ai-slop-gate.readthedocs.io/>`_