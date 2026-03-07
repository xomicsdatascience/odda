# ODDA - Omics Data Discovery Agents

ODDA uses AI agents and MCP (Model Context Protocol) servers to parse scientific articles, extract metadata, download omics datasets, and run quantification pipelines. It provides an end-to-end workflow from literature discovery to data analysis.

## Table of Contents

- [Architecture](#architecture)
- [Expected Data Layout](#expected-data-layout)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Architecture

The system is composed of **MCP servers** that expose tool endpoints and **agents** that orchestrate multi-step tasks by calling those tools.

### MCP Servers

| Package | Description |
|---|---|
| `odda_utils` | Article management, metadata extraction, dataset downloads, supplemental classification, embedding search |
| `odda_diann` | DIA-NN quantification via Apptainer containers |
| `odda_maxquant` | MaxQuant quantification via Apptainer containers |
| `odda_thermofisher` | ThermoRawFileParser for raw file conversion via Apptainer containers |

### Agents

| Agent | Purpose |
|---|---|
| `article-processor` | Fetches scientific articles, extracts metadata, and validates database integrity |
| `dataset-processor` | Downloads omics datasets from public repositories (GEO, ProteomeXchange, iProX, MassIVE) and catalogs their contents |
| `supplemental-classifier` | Classifies supplemental materials into categories (raw data, quantitative data, summary data, supporting) |
| `omics-quantifier` | Runs quantification pipelines (DIA-NN, MaxQuant) on raw instrument data |
| `omics-analyzer` | Performs QC, differential expression, and enrichment analysis on quantified data |
| `mcp-feature-developer` | Implements new MCP server features and endpoints |

### Additional Components

| Package | Description |
|---|---|
| `request_visualization` | PyQt6 desktop GUI for visualizing and managing agent requests |

## Expected Data Layout

```
/data/
  articles/        # Downloaded articles and supplemental materials
  datasets/        # Raw datasets, named by dataset ID
  quantified/      # Quantification results, versioned (v0/, v1/, ...)
  supporting/      # Shared files (e.g. FASTA databases)
  code/            # Code repositories
```

## Requirements

- Python >= 3.11
- Apptainer (for containerized quantification tools)

## Installation

We use Apptainer containers for executing tools; for installation of ODDA, we assume that it is installed on your system. If it isn't, please see [Apptainer's installation instructions](https://apptainer.org/docs/admin/main/installation.html).

ODDA uses git submodules to track the separate components independently. To obtain the required files, use the `--recursive` flag when clone the repository. The `install.sh` script can then be used to set up the environment and dependencies:

```bash
git clone --recursive git@github.com:xomicsdatascience/odda odda
cd odda
./install.sh
```

Due to license restrictions, we are unable to distribute the underlying software (DIA-NN, MaxQuant) to simplify installation. You will need to download these separately; links and instructions are provided below for each component. Ensure that you meet the license terms for these, as some have specific restrictions about usage.

- **DIA-NN** : [Download the DIA-NN binaries](https://github.com/vdemichev/DiaNN/releases/tag/2.0) and place them in `odda_diann/static/apptainer/`.
- **MaxQuant** : [Download the MaxQuant files](https://maxquant.org/download_asset/maxquant/latest) and place them in `odda_maxqaunt/static/apptainer/`.
- **ThermoFisherFileParser** : [Download the ThermoRawFileParser](https://github.com/CompOmics/ThermoRawFileParser/releases), "ThermoRawFileParser-v.2.0.0-dev-linux.zip" and place it in `odda_thermofisher/static/apptainer/`

Once done, run the `build_mcp_images.sh`. The script will create Apptainer containers for the versions of the software you downloaded. Once done, you can run the `start_all_instances.sh` script to launch all Apptainer instances.

### Summary
1. Install Apptainer.
2. git clone recursively
3. Download DIA-NN, MaxQuant, ThermoFisherFileParser.
4. Build images using `build_mcp_images.sh`
5. Start instances of the images using `start_all_instances.sh`

## Usage

ODDA is designed to be used through an MCP-compatible AI client (e.g. Claude Code). The MCP servers are configured in `.mcp.json` and agents are defined in `.claude/agents/`. Interact with the system by describing tasks in natural language - the orchestrator delegates to the appropriate agent and MCP tools.

Example prompts:

- *"Search for liver fibrosis proteomics articles published in 2024"*
- *"Download the dataset PXD012345 and classify its contents"*
- *"Run DIA-NN quantification on PXD012345 using library-free mode"*
- *"Compare protein expression between treated and control samples"*

## License

GPLv3
