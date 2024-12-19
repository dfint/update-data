# Update Data

Data backend for [dfint installer](https://github.com/dfint/installer).

- [`metadata/hook_v2.json`](metadata/hook_v2.json) contains info about releases of [df-steam-hook-rs](https://github.com/dfint/df-steam-hook-rs), info about [dfhooks](https://github.com/DFHack/dfhooks) library, configs, offset files for installer 0.2.0 and higher
- [`metadata/dict.json`](metadata/dict.json) contains info about localization languages: url of their csv files, font files, encoding specific configs
- [`store`](store) directory contains files referenced from metadata, like encoding specific configs, offsets for different DF versions, and other misc. stuff.

Legacy, not updated anymore:

- [`metadata/hook.json`](metadata/hook.json) contains metadata for installer older then 0.2.0.
