# discmos

**Generates a mosaic of Discord emojis that matches an image.**

## Installation

**Install with `python3 -m pip install git+https://github.com/liamgd/discmos.git`.**

In its current state, this tool only works with Windows. To make it compatible with macOS and Linux:

1. Clone this repository.
2. Remove all instances of win32clipboard and copying in the composite function in cli.py.
3. Install the package directly from the cloned repository (use --editable if you want to make frequent tweaks).

## Usage

Run `discmos --help` to see a list of commands. Run `discmos <command> --help` to see command options.

**The workflow generally looks like:**

1. Install discmos.
2. Run `discmos init-workspace ./discmos-workspace/`.
3. Run `discmos scrape` and choose to copy the script and open the Discord website.
4. Follow the instructions printed from `discmos scrape` to save the emoji-data.json file to the workspace directory.
5. Run `discmos download-all`. This step can be performed after step 6 if you only want to download the emojis you intend to use right away.
6. Adjust the include.txt file as necessary to determine which emojis to include in the mosaic.
7. Use `discmos preview-include ./discmos-workspace/` to verify that the correct emojis are included.
8. Run `discmos --save --show ./discmos-workspace/ source.jpg 40 8 composite 1000` (adjusting the parameters if desired) to show the mosaic, copy it to the clipboard, and save it to the output-images directory.

## Computation Implementation

After downloading, to remove transparency, the emoji files are saved over a background that is the same color as the Discord background on the desktop app.

The emoji image files in the emojis directory are rescaled to a low resolution for performance and converted into PyTorch tensors.

The source image is split into tiles that are the same size as the emojis after rescaling. These tiles are also converted into PyTorch tensors.

The emoji tensors are stacked and the source image tensors are stacked to create two tensors of the shape (tile, channel, height, width). The channels represent the hue, saturation, and value for each pixel.

After further processing, using singleton dimension slicing and operation broadcasting, the difference between the channel values of the pixels of each pair of emoji and source image tile is found. The absolute value is taken so that lower values correspond to less difference between pixel colors. Using singleton dimension slicing, the resulting tensor is multiplied element-wise by a channel weights tensor to control the importance hue, saturation, and value individually. The difference values for each pair of emoji and source image tile are summed to obtain one value that represents the difference between the two image tiles. After flattening, the argmin function is used to determine the emoji that is closest to the source image tile for every source image tile in the source image.

## GPU Acceleration

If a CUDA-enabled GPU is available, the tensors in the computation will use the CUDA device. If not, the CPU is used instead.

## Emoji Scraping

The following instructions are printed upon running `discmos scrape`. The emojis are scraped by executing a javascript script in the console pane of the inspect element that saves emojis as they appear while scrolling in the Discord emoji pane.

Steps to scrape emojis:

1. Ensure that you have initialized a workspace directory with discmos init-workspace prior to scraping emojis.
2. Copy the javascript console script (console.js on github.com).
3. Open the Discord website app in the browser and navigate to a server or direct message where you can type a message.
4. Open the inspect element on the website (control-shift-C or command-option-C).
5. Navigate to the console pane in the inspect element.
6. Paste the javascript console script and press enter to initiate it. Until done, do not press any key on the keyboard.
7. Click to open the emoji pane to the right of the text input bar on the bottom of the screen.
8. Scroll up and down in the emoji pane until all custom server emojis have appeared at least once (emoji names should appear in the console).
9. Press any key on the keyboard (ex. space) or type "save()" in the console.
10. Save emoji-data.json in the workspace directory.
11. You are done, and you can close the Discord tab.

## Composite Mosaic

**This is how the Discord character limit that complicates sending the mosaic in emoji messages is bypassed.**

The composite mosaic can be run with `discmos mosaic [--OPTIONS] [ARGUMENTS] composite IMAGE-WIDTH`, where the width to which the final image is upscaled or downscaled is set as `IMAGE-WIDTH`.

After computation, it will copy the image file containing the emoji mosaic to the clipboard (Windows only). The `--save` option saves the image as a PNG in `<workspace>/output-images`. The `--show` option opens a window to preview the image.

There is no gap between emojis, unlike when multiple emoji messages are sent on Discord.

## Text Mosaic

The text mosaic can be run with `discmos mosaic [--OPTIONS] [ARGUMENTS] text`.

After computation, it will copy the text containing the emoji mosaic to the clipboard. The `--save` option saves the text to a file in `<workspace>/output-text`. The `--show` option prints the text in the terminal.

To render the text into a mosaic image, paste it into discord. See the Discord Nitro section. If character count becomes an issue, paste fewer lines in multiple messages to show the full image. Note that there is a small gap between each message.

## Discord Nitro

All custom emojis from all servers will be scraped from Discord, regardless of Discord Nitro status.

If you would like to message the text variant of the mosaic that uses emojis from another server, Discord Nitro is required. Also, Discord Nitro increases the maximum character count, allowing for longer lines to be sent.

## Requirements

See the requirements.txt file.

Requirements file generated with `pipreqs --mode compat --force`, with `pywin32` removed.
