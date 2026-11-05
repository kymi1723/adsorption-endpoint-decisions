# What to upload to GitHub

Use the **contents** of `adsorption_endpoint_release/` as the repository root. Its top level should contain `README.md`, `LICENSE`, `LICENSE_SCOPE.md`, `run_release.py`, `requirements-lock.txt`, `endpoint_release/`, `tools/` and the intended reproducibility assets. Avoid an unnecessary extra nested `adsorption_endpoint_release/` level. Do not upload the whole research workspace.

For the full source snapshot, use Git or GitHub Desktop to preserve directory structure and `.gitignore`. GitHub's browser uploader accepts at most100 files per upload and25MiB per individual file; this snapshot has more than100 files, so a single browser batch is unsuitable. Keep `.gitignore` included; do not add a virtual environment, generated `outputs/`, local wheelhouse or working history.

The sibling `adsorption_endpoint_release.zip` is an equivalent downloadable snapshot with one enclosing directory. It is suitable as a GitHub **Release asset**, in addition to the expanded repository source. Merely uploading the ZIP as a repository file leaves the source inside that archive; it does not create the readable source tree. You do not need to commit both the ZIP and expanded files to the source branch.

The local folder and ZIP are identical at the verification snapshot recorded in `release_license_report.md` outside this package. Once someone edits the folder or runs commands that add output files, it no longer necessarily matches that old ZIP; regenerate an intentional release ZIP after reviewing those changes. `provenance/file_manifest.json` lists the distributable snapshot files, excluding itself.

The original code is now MIT-licensed; non-code rights remain distinguished in `LICENSE_SCOPE.md`. Decide which research assets may be publicly redistributed under their applicable terms before posting the full snapshot. This is not solved by labelling all repository contents MIT.

No GitHub account, repository, commit, remote push or Release was created by this local task. No example repository address is substituted for a real one.

Official references (checked2026-11-05):

- [GitHub: adding files](https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository)
- [GitHub: licensing a repository](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository)
- [GitHub: release assets](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository)
- [MIT standard text](https://opensource.org/license/mit)
