# General description
This project provides MCP servers for agents to fetch scientific articles and extract metadata related to the article's research topic, datasets, and analysis methods. Additionally, it provides access to omic quantification methods (DIA-NN, MaxQuant).

# Project parameters
The following information can be found in the following files/directories:

- Articles and supplementals can be found in `/data/articles/` - new articles and supplementals should be placed here.
- Downloaded datasets can be found in `/data/datasets/` - they are named using their dataset ID.
- Quantified datasets can be found in `/data/quantified/` - they are named using their source dataset ID. 
-- Each directory can contain different versions (e.g. v0/, v1/, v2/).
-- New quantifications should create a new subdirectory to place files into.
- Supporting files can be found in `/data/supporting/` - these are for files that span across experiments such as FASTA files.
-- If external files are downloaded that are not unique to a dataset, they should be placed in this directory.
- Azure credentials can be found in `.claude/` (azure.key, azure.endpoint)
- Code repositories can be found in `/data/code/`
- For MCP functions that require specifying an LLM model for Azure, use the default value if available. Otherwise, use one of the following models for general-purpose parsing: gpt-5, gpt-5.1, gpt-5.2. For embeddings, use text-embedding-3-small.
- When using Python, use the virtual environment in `.venv/`

# Delegation
- Verify whether there is an agent that would be suitable for a given request and delegate if so. If no agent matches the task, communicate this to the user and request confirmation before proceeding on your own.
- Pass the project parameters (paths, credentials) to agents in addition to the task specification.
- When delegating, describe what needs to be done but do not give instructions on how implement a solution. Agents have been given their own instructions and your instructions could conflict with the ones they have received.

# Coding instructions
- Use Python; double-check with the user if other languages are needed (e.g. due to language-specific packages).
- When writing docstrings, use the NumPy format.
- In each Python file, include a comment at the start of the file summarizing the purpose of the file contents. When there is no comment, parse the file and add one.
- Instead of executing Python code directly, create a temporary directory, write the code to a file, then execute the file.

# MCP servers
Multiple tools are made available to you via MCP servers. If no agent is found to complete a task, try to use MCP functionality before attempting custom solutions.
