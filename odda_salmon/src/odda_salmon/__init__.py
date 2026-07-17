# Salmon MCP server module - provides MCP tools for running Salmon via Apptainer.
#
# This module defines the Salmon RNA-seq quantification MCP server package which
# exposes tools for:
# - Building a Salmon transcriptome index (salmon index)
# - Quantifying RNA-seq reads (salmon quant)
# - Listing available Salmon versions from built salmon_v*.sif images and any
#   running Apptainer instances
# - Describing Salmon's command-line arguments
#
# Salmon images follow the naming convention salmon_v{version}.sif and, for
# parity with the other quantification servers, the instance naming convention
# instance://salmon_v{version}. Because `apptainer instance start` is broken on
# the deployment host, the run/index tools execute the container directly.
__version__ = "0.1.0"

# Instance URI format (used only by version discovery for parity with the other
# servers; the run/index tools execute the .sif directly).
salmon_instance_format = "instance://salmon_v{version}"

# On-disk image name format for a given Salmon version.
salmon_sif_format = "salmon_v{version}.sif"

salmon_all_arguments = """
Salmon is invoked with a subcommand: `index` builds a transcriptome index and
`quant` quantifies RNA-seq reads against that index.

=== salmon index ===
-t, --transcripts VALUE   Transcript FASTA file to index (required).
-i, --index VALUE         Output directory in which to write the salmon index (required).
-k, --kmerLen VALUE       Size of the k-mers used to build the index (default 31); 31 is recommended for reads >= 75 bp.
-p, --threads VALUE       Number of threads to use while building the index.
-d, --decoys VALUE        Path to a text file listing decoy sequence names (e.g. genome targets) for a decoy-aware index.
--keepDuplicates          Retain duplicate (identical) transcript sequences instead of collapsing them.
--gencode                 Expect a GENCODE-format transcript FASTA and split headers on the '|' character.
--features                Build the index from a features file rather than a transcript FASTA.
-s, --sparse              Build a sparser index that uses less memory at some cost to lookup speed.
-n, --no-clip             Do not clip poly-A tails from the ends of the target sequences.
--type VALUE              Type of index to build (only 'puff' is supported by current Salmon versions).

=== salmon quant (mapping-based mode) ===
-i, --index VALUE         Path to the Salmon index directory (required).
-l, --libType VALUE       Library type string; use 'A' to let Salmon infer it automatically (required).
-r, --unmatedReads VALUE  Space-separated list of files containing unmated (single-end) reads.
-1, --mates1 VALUE        Space-separated list of files containing the #1 mates of paired-end reads.
-2, --mates2 VALUE        Space-separated list of files containing the #2 mates of paired-end reads.
-o, --output VALUE        Output directory for the quantification results (required).
-p, --threads VALUE       Number of threads to use during quantification.
--seqBias                 Enable modelling and correction of sequence-specific bias.
--gcBias                  Enable modelling and correction of fragment-level GC bias.
--posBias                 Enable modelling and correction of positional bias.
--validateMappings        Validate mappings using selective alignment (default in recent versions; accepted for compatibility).
--recoverOrphans          Attempt to recover the mates of orphaned mappings via alignment.
--numBootstraps VALUE     Number of bootstrap samples to draw for quantification uncertainty estimation.
--numGibbsSamples VALUE   Number of Gibbs sampling rounds to draw for quantification uncertainty estimation.
-g, --geneMap VALUE       File mapping transcripts to genes; enables gene-level (quant.genes.sf) output.
--meta                    Enable metagenomic mode.
--fldMean VALUE           Expected mean fragment length (used for single-end libraries).
--fldSD VALUE             Expected standard deviation of the fragment length distribution (single-end libraries).
--writeMappings VALUE     Write the read mappings, in SAM format, to the given file (or stdout when omitted).
--minScoreFraction VALUE  Minimum alignment score, as a fraction of the maximum possible, for a mapping to be retained.
--rangeFactorizationBins VALUE  Number of range-factorization bins used to improve multi-mapping quantification.
--useEM                   Use the standard EM algorithm instead of the default variational Bayesian optimiser.
--dumpEq                  Dump the equivalence-class counts to the auxiliary directory.
--noLengthCorrection      Disable transcript-length correction (e.g. for 3'-tagged libraries).
"""

salmon_argument_dict = {
    # --- salmon index ---
    "-t": "salmon index: Transcript FASTA file to index (required).",
    "--transcripts": "salmon index: Transcript FASTA file to index (required).",
    "transcripts": "salmon index: Transcript FASTA file to index (required).",
    "-i": "Path to the Salmon index directory. For `index` this is the output location; for `quant` it is the existing index to read (required).",
    "--index": "Path to the Salmon index directory. For `index` this is the output location; for `quant` it is the existing index to read (required).",
    "index": "Path to the Salmon index directory. For `index` this is the output location; for `quant` it is the existing index to read (required).",
    "-k": "salmon index: Size of the k-mers used to build the index (default 31); 31 is recommended for reads >= 75 bp.",
    "--kmerLen": "salmon index: Size of the k-mers used to build the index (default 31); 31 is recommended for reads >= 75 bp.",
    "kmerLen": "salmon index: Size of the k-mers used to build the index (default 31); 31 is recommended for reads >= 75 bp.",
    "-d": "salmon index: Path to a text file listing decoy sequence names (e.g. genome targets) for a decoy-aware index.",
    "--decoys": "salmon index: Path to a text file listing decoy sequence names (e.g. genome targets) for a decoy-aware index.",
    "decoys": "salmon index: Path to a text file listing decoy sequence names (e.g. genome targets) for a decoy-aware index.",
    "--keepDuplicates": "salmon index: Retain duplicate (identical) transcript sequences instead of collapsing them.",
    "keepDuplicates": "salmon index: Retain duplicate (identical) transcript sequences instead of collapsing them.",
    "--gencode": "salmon index: Expect a GENCODE-format transcript FASTA and split headers on the '|' character.",
    "gencode": "salmon index: Expect a GENCODE-format transcript FASTA and split headers on the '|' character.",
    "--features": "salmon index: Build the index from a features file rather than a transcript FASTA.",
    "features": "salmon index: Build the index from a features file rather than a transcript FASTA.",
    "-s": "salmon index: Build a sparser index that uses less memory at some cost to lookup speed.",
    "--sparse": "salmon index: Build a sparser index that uses less memory at some cost to lookup speed.",
    "sparse": "salmon index: Build a sparser index that uses less memory at some cost to lookup speed.",
    "-n": "salmon index: Do not clip poly-A tails from the ends of the target sequences.",
    "--no-clip": "salmon index: Do not clip poly-A tails from the ends of the target sequences.",
    "no-clip": "salmon index: Do not clip poly-A tails from the ends of the target sequences.",
    "--type": "salmon index: Type of index to build (only 'puff' is supported by current Salmon versions).",
    "type": "salmon index: Type of index to build (only 'puff' is supported by current Salmon versions).",
    # --- salmon quant ---
    "-l": "salmon quant: Library type string; use 'A' to let Salmon infer it automatically (required).",
    "--libType": "salmon quant: Library type string; use 'A' to let Salmon infer it automatically (required).",
    "libType": "salmon quant: Library type string; use 'A' to let Salmon infer it automatically (required).",
    "-r": "salmon quant: Space-separated list of files containing unmated (single-end) reads.",
    "--unmatedReads": "salmon quant: Space-separated list of files containing unmated (single-end) reads.",
    "unmatedReads": "salmon quant: Space-separated list of files containing unmated (single-end) reads.",
    "-1": "salmon quant: Space-separated list of files containing the #1 mates of paired-end reads.",
    "--mates1": "salmon quant: Space-separated list of files containing the #1 mates of paired-end reads.",
    "mates1": "salmon quant: Space-separated list of files containing the #1 mates of paired-end reads.",
    "-2": "salmon quant: Space-separated list of files containing the #2 mates of paired-end reads.",
    "--mates2": "salmon quant: Space-separated list of files containing the #2 mates of paired-end reads.",
    "mates2": "salmon quant: Space-separated list of files containing the #2 mates of paired-end reads.",
    "-o": "salmon quant: Output directory for the quantification results (required).",
    "--output": "salmon quant: Output directory for the quantification results (required).",
    "output": "salmon quant: Output directory for the quantification results (required).",
    "-p": "Number of threads to use (applies to both `index` and `quant`).",
    "--threads": "Number of threads to use (applies to both `index` and `quant`).",
    "threads": "Number of threads to use (applies to both `index` and `quant`).",
    "--seqBias": "salmon quant: Enable modelling and correction of sequence-specific bias.",
    "seqBias": "salmon quant: Enable modelling and correction of sequence-specific bias.",
    "--gcBias": "salmon quant: Enable modelling and correction of fragment-level GC bias.",
    "gcBias": "salmon quant: Enable modelling and correction of fragment-level GC bias.",
    "--posBias": "salmon quant: Enable modelling and correction of positional bias.",
    "posBias": "salmon quant: Enable modelling and correction of positional bias.",
    "--validateMappings": "salmon quant: Validate mappings using selective alignment (default in recent versions; accepted for compatibility).",
    "validateMappings": "salmon quant: Validate mappings using selective alignment (default in recent versions; accepted for compatibility).",
    "--recoverOrphans": "salmon quant: Attempt to recover the mates of orphaned mappings via alignment.",
    "recoverOrphans": "salmon quant: Attempt to recover the mates of orphaned mappings via alignment.",
    "--numBootstraps": "salmon quant: Number of bootstrap samples to draw for quantification uncertainty estimation.",
    "numBootstraps": "salmon quant: Number of bootstrap samples to draw for quantification uncertainty estimation.",
    "--numGibbsSamples": "salmon quant: Number of Gibbs sampling rounds to draw for quantification uncertainty estimation.",
    "numGibbsSamples": "salmon quant: Number of Gibbs sampling rounds to draw for quantification uncertainty estimation.",
    "-g": "salmon quant: File mapping transcripts to genes; enables gene-level (quant.genes.sf) output.",
    "--geneMap": "salmon quant: File mapping transcripts to genes; enables gene-level (quant.genes.sf) output.",
    "geneMap": "salmon quant: File mapping transcripts to genes; enables gene-level (quant.genes.sf) output.",
    "--meta": "salmon quant: Enable metagenomic mode.",
    "meta": "salmon quant: Enable metagenomic mode.",
    "--fldMean": "salmon quant: Expected mean fragment length (used for single-end libraries).",
    "fldMean": "salmon quant: Expected mean fragment length (used for single-end libraries).",
    "--fldSD": "salmon quant: Expected standard deviation of the fragment length distribution (single-end libraries).",
    "fldSD": "salmon quant: Expected standard deviation of the fragment length distribution (single-end libraries).",
    "--writeMappings": "salmon quant: Write the read mappings, in SAM format, to the given file (or stdout when omitted).",
    "writeMappings": "salmon quant: Write the read mappings, in SAM format, to the given file (or stdout when omitted).",
    "--minScoreFraction": "salmon quant: Minimum alignment score, as a fraction of the maximum possible, for a mapping to be retained.",
    "minScoreFraction": "salmon quant: Minimum alignment score, as a fraction of the maximum possible, for a mapping to be retained.",
    "--rangeFactorizationBins": "salmon quant: Number of range-factorization bins used to improve multi-mapping quantification.",
    "rangeFactorizationBins": "salmon quant: Number of range-factorization bins used to improve multi-mapping quantification.",
    "--useEM": "salmon quant: Use the standard EM algorithm instead of the default variational Bayesian optimiser.",
    "useEM": "salmon quant: Use the standard EM algorithm instead of the default variational Bayesian optimiser.",
    "--dumpEq": "salmon quant: Dump the equivalence-class counts to the auxiliary directory.",
    "dumpEq": "salmon quant: Dump the equivalence-class counts to the auxiliary directory.",
    "--noLengthCorrection": "salmon quant: Disable transcript-length correction (e.g. for 3'-tagged libraries).",
    "noLengthCorrection": "salmon quant: Disable transcript-length correction (e.g. for 3'-tagged libraries).",
}
