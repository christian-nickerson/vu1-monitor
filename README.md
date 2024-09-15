# VU1-Monitor

A CLI application for monitoring hardware using [VU1 Dials](https://streacom.com/products/vu1-dynamic-analogue-dials/)

## What is this?

The VU1 Dials come with a server application and demo monitoring app out of the box. The Demo app is set up to work on Windows machines only. This application fills this gap for both MacOS and Linux users that want to monitor their hardware using the VU1 Dials.

## Quickstart

### Prerequisites

1. To install `vu1-monitor` it is recommended to use `pipx` to instal the tool.

    `pipx` is used to install Python CLI applications globally while still isolating them in virtual environments. `pipx` will manage upgrades and uninstalls of `vu1-monitor`. If `pipx` is not already installed, you can follow any of the options in the official [pipx installation instructions](https://pipx.pypa.io/stable/installation/).

2. `vu1-monitor` is a python CLI application and supports 3.10+
3. `vu1-monitor` is a "VU" application and expects the `vu-server` to be running

    To run `vu-server`, you can follow the [instructions to install and run the application](https://vudials.com/)

### Install

To install `vu1-monitor` run the following:

```bash
pipx install vu1-monitor
```

### Start monitoring

To start monitoring, you can run the following:

```bash
vu1-monitor run
```

## Commands

`vu1-monitor` provides several utilities for interacting and configuring your VU1-Dials

### Run

`vu1-monitor` by default will only update the CPU dial. Run can also update other dials and alter the update interval speed:

```bash
# runs all available dials, including CPU
vu1-monitor run --gpu --mem --net

# runs all dials, except CPU
vu1-monitor run --no-cpu --gpu --mem --net

# updates dials every second
vu1-monitor run --interval 1
```

### Backlight

`vu1-monitor` provides a series of pre-set backlight colours and brightness profiles for each / all dials.

```bash
# set the CPU dial to its default colour and brightness (LOW & WHITE)
vu1-monitor backlight --dial CPU

# sets the GPU dial backlight to red, at its maximum brightness
vu1-monitor backlight --dial MEMORY --colour RED --brightness MAX
```

### Image

`vu1-monitor` provides a utility to upload background images to each dial:

```bash
### sets the background image of the network dial to your supplied png

vu1-monitor image /your/file/path/dial.png --dial NETWORK
```

> [!NOTE]
> VU1 Dials expect their background images to be either in `.png` or `.jpg` formats and must be exactly 200 x 144 pixels. `vu1-monitor` and the `vu-server` are strict about this requirement and will reject anything outside of this

### Reset

`vu1-monitor` provides a utility to reset each element (dial, backlight, image) of all dials:

```bash
# reset the position of a dial to 0
vu1-monitor reset dial

# reset the backlight of a dial to OFF
vu1-monitor reset backlight

# reset the image to default vu1-monitor images
vu1-monitor reset image
```

## Configuration

`vu1-monitor` is set up to work with the default configurations of `vu-server`. However, these configurations can be overridden using environment variables. `vu1-monitor` looks for environment variables by looking for the prefix `VU1`.

| Environment Variable Name | Description | Default Value |
| :--- | :--- | :--- |
| `VU1__SERVER__HOSTNAME` | The hostname of the VU-Server | `localhost` |
| `VU1__SERVER__PORT` | The port of the VU-Server | 5430 |
| `VU1__SERVER__LOGGING_LEVEL` | The logging level of VU1-Monitor | `INFO` |
| `VU1__SERVER__KEY` | The API key to authenticate with VU-Server. The default value is the default value of VU-Server, please generate a new key in the VU UI Console and set as your new key | `cTpAWYuRpA2zx75Yh961Cg` |
| `VU1__CPU__NAME` | The name of the Dial assigned to CPU monitoring | `CPU` |
| `VU1__GPU__NAME` | The name of the Dial assigned to GPU monitoring | `GPU` |
| `VU1__MEMORY__NAME` | The name of the Dial assigned to Memory monitoring | `MEMORY` |
| `VU1__NETWORK__NAME` | The name of the Dial assigned to Network monitoring | `NETWORK` |

> [!NOTE]
> `vu1-monitor` identifies specific Dials by their name, as configured in `vu-server`. Please make sure that each dial name matches what is expected by `vu1-monitor`

## Supported hardware

`vu1-monitor` supports OS agnostic tooling, particularly across Linux, MacOS & Linux. However, `vu1-monitor` is only tested and maintained on MacOS & Linux (`vu-server` had a default demo app for windows).

Currently, `vu1-monitor` supports NVIDIA GPU monitoring only. AMD & Apple GPU monitoring will be coming in later releases.
