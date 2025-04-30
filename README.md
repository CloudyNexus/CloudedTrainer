# CloudedTrainer

An open-source Linux-based WeMod alternative for Ubuntu that auto-detects games and provides working trainers with a modern GUI.

![CloudedTrainer](https://github.com/user-attachments/assets/c08aba1b-25c7-43bd-a5d4-bf081d745b10)

## Overview

CloudedTrainer is a free and open-source game trainer for Ubuntu and other Linux distributions. It's designed to be a Linux alternative to tools like WeMod, offering gamers the ability to enhance their single-player gaming experience with trainers (cheats) that work natively on Linux.

### Key Features

- **Auto Game Detection:** Automatically finds installed games from Steam, Lutris, and other platforms
- **Working Trainers:** Includes functional trainers for popular games
- **Modern UI:** Clean, intuitive interface built with Flask and Bootstrap
- **Memory Manipulation:** Uses ptrace and other Linux system calls to modify game memory
- **Open Source:** Free and open-source under GPL-3.0
- **Platform Support:** Works with Steam games and other common game platforms on Ubuntu

## Supported Games

Currently includes trainers for:

- Counter-Strike: Global Offensive
- Dota 2
- Team Fortress 2
- Minecraft
- Terraria

More games will be added in future updates!

## Installation

### Prerequisites

- Python 3.8+
- Ubuntu 20.04+ or compatible Linux distribution
- Administrative privileges (for memory access)

### Install from Source

1. Clone the repository:

```bash
git clone https://github.com/openlinuxtrainer/openlinuxtrainer.git
cd openlinuxtrainer
