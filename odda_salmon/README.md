# Salmon MCP server

The repository holds code for building Apptainer images of Salmon and making the
RNA-seq quantification tool available via an MCP server. It adds a
transcriptomics quantification capability that complements the proteomics tools
(DIA-NN, MaxQuant, ThermoRawFileParser).

## Tools

- `list_salmon_versions` - discover available Salmon versions from the built
  `salmon_v*.sif` images (and any running Apptainer instances).
- `build_salmon_index` - build a transcriptome index with `salmon index`.
- `run_salmon` - quantify paired- or single-end RNA-seq reads with `salmon quant`.
- `get_salmon_argument_info` - describe Salmon's `index`/`quant` arguments.

The run/index tools execute the container directly with
`apptainer run <salmon_vX.sif> <args>` because `apptainer instance start` is not
available on the deployment host.

## Building images

```bash
static/apptainer/build_images.sh
```
