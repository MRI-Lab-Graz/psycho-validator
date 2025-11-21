# BIDS-Apps Workflow for PRISM

PRISM datasets use a rich, nested metadata structure that is not directly compatible with standard BIDS-Apps (like fMRIPrep, MRIQC, etc.). 

To use these tools, you must create a **BIDS Snapshot**—a temporary, BIDS-compliant view of your data.

## The Workflow

1.  **Create Snapshot**: Generate a temporary BIDS version of your dataset.
2.  **Run BIDS-App**: Run the tool (e.g., fMRIPrep) on the snapshot.
3.  **Collect Results**: The output (derivatives) is standard BIDS and can be kept.
4.  **Cleanup**: Delete the snapshot.

## 1. Creating a Snapshot

Use the `scripts/bids_snapshot.py` tool. It uses **hardlinks** for data files (NIfTI, TSV), so it is:
*   **Fast**: Takes seconds, even for large datasets.
*   **Lightweight**: Uses almost no additional disk space.
*   **Safe**: Modifying the snapshot's metadata does *not* affect your source data.

```bash
# Syntax: python3 scripts/bids_snapshot.py <source_dataset> <snapshot_path>

python3 scripts/bids_snapshot.py my_study/ data/scratch/my_study_bids
```

## 2. Running fMRIPrep

Point fMRIPrep to the **snapshot directory**.

```bash
# Example using fmriprep-docker
fmriprep-docker \
    data/scratch/my_study_bids \
    my_study/derivatives \
    participant
```

*   **Input**: `data/scratch/my_study_bids` (The snapshot)
*   **Output**: `my_study/derivatives` (Your real dataset's derivatives folder)

## 3. Cleanup

Once the processing is done, you can safely remove the snapshot directory.

```bash
rm -rf data/scratch/my_study_bids
```

## Why not just convert the main dataset?

You *can* use `prism-convert.py --to-bids` on your main dataset, run the app, and then convert back. However, this carries risks:
*   If the conversion isn't perfectly reversible, you might lose metadata.
*   If you forget to convert back, your dataset remains in "flat" mode.
*   Git/DataLad might detect changes to every JSON file, creating noise in your history.

The snapshot approach is safer and cleaner.
