## Contribute

1. open an issue
1. make a fork of this repo
1. make your changes
1. test it (manual because right now their a no automated tests)
1. make a pull request
1. wait for approval

### Setting up your development machine

> Note for the easy documentation only the dev container way is described here. If you want to develop nativ on you PC good luck for now

You need:

- [VsCode](https://code.visualstudio.com/)
- [Dev Containers Extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
- some container engine that is supported by Dev Containers Extension for example Docker

Starting Development

1. Start an empty VsCode
1. Press `STRG` + `SHIFT` + `P`
1. Select `Dev Containers: Clone Repository in Container Volume...`
1. Provide the URL of your fork
1. Wait (depending on your internet connection and PC this step can take more then half an hour, only the first time)
1. Press `STRG` + `SHIFT` + `P`
1. Select `Tasks: Run Task`
1. Select `Reset homeassistant`
1. Now you can select in the Debugger of VsCode `Home Assistant` (this will again run for a while)
1. Now you should have a running instance of Home Assistant and you can access it on your host via `http://127.0.0.1:8123/`

If you want to debug again after the first start we recommend using `Home Assistant (skip pip)` because it's way faster.

After you finished your main work we recommend to run the task `Generate Docs`:

1. Press `STRG` + `SHIFT` + `P`
1. Select `Tasks: Run Task`
1. Select `Generate Docs`

This will update the device documentation.
