# Forge Source Layout

`build_forge.py` is the compiler. It builds the root `forge` executable from smaller source files.

Authoring locations:

- `build_forge.py`: compiler, stage metadata, agent contracts, gate contracts.
- `runtime/forge_cli.py.tmpl`: generated root CLI template.
- `runtime/server.py`: dashboard API server copied to `.forge/scripts/server.py`.
- `runtime/build_runner.py`: build-system runner copied to `.forge/scripts/build_runner.py`.
- `dashboard/index.html`: dashboard document shell.
- `dashboard/styles.css`: dashboard styles.
- `dashboard/scripts/*.js`: ordered dashboard client behavior.
- `dashboard/scripts.txt`: script assembly order.
- `dashboard.html`: generated compatibility snapshot assembled from `dashboard/*`.

Do not hand-edit `dashboard.html` for source changes. Edit `dashboard/*`, then run:

```sh
python3 src/build_forge.py
./forge upgrade
```

The runtime contract is still a single `forge` artifact plus generated `.forge/scripts/*` files.
