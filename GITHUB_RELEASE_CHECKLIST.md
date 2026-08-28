# GitHub Release Checklist

## Required edits

- [ ] Replace `YOUR_GITHUB_USERNAME` in `README.md` and `pyproject.toml`.
- [ ] Replace `YOUR_COMFY_PUBLISHER_ID` in `pyproject.toml` if publishing to the Comfy Registry.
- [ ] Replace the copyright holder in `LICENSE` if desired.
- [ ] Confirm no checkpoint, LoRA, API key, private image, or restricted asset is included.

## Verification

- [ ] Run `python test_node.py`.
- [ ] Copy the repository to `ComfyUI/custom_nodes` and restart ComfyUI.
- [ ] Load the example JSON and reselect locally available checkpoint/LoRA names.
- [ ] Queue one image and confirm both `lettered_page` and `bubble_mask` outputs.

## Suggested GitHub commands

```bash
git init
git add .
git commit -m "Initial release: deterministic four-panel comic lettering"
git branch -M main
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/ComfyUI-IllustriousComicLettering.git
git push -u origin main
```

Suggested release tag: `v1.0.0`.

For an optional Registry release, create a Comfy publisher, replace the publisher placeholder, then run `comfy node publish`. Never commit the Registry API key.
