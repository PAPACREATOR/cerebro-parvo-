# Pinokio source adaptation

The explicit hand-off in `nexus/ui/app.js`, `composedStepRequest`, adapts the fresh parameter-object merge used by `Script.buildStartRequest`:

- Repository: <https://github.com/pinokiocomputer/pinokiod>
- Source: <https://github.com/pinokiocomputer/pinokiod/blob/add4a674ad1ba95bb62ec427fce519fe5bf0e9bf/kernel/api/script/index.js>
- Fixed commit: `add4a674ad1ba95bb62ec427fce519fe5bf0e9bf`
- The engine's `package.json` declares the MIT license.
- The accompanying `LICENSE` reproduces the Pinokio MIT notice, Copyright 2023 Pinokio, from the fixed desktop source <https://github.com/pinokiocomputer/pinokio/blob/0765ab1c24eee9bf7acf1618b94e1cfdc52886fc/LICENSE>.

The adaptation constructs a fresh request from the captured Folha input and the selected command. It retains immutable original bytes and validates the preceding tool result before proposing the next step. The next operation goes through the existing, separate human confirmation.

This is a small source adaptation. Pinokio's script executor, arbitrary URI/script selection, downloads, session inheritance, shell execution, runtime and dependencies are not included. This notice does not license third-party dependencies of either project.
