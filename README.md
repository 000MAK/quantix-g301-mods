# Quantix G301 mods

Boot screen, Magisk modules and setup notes for a **General Mobile G301** (MediaTek MT6765, Android 11).

| Path | What |
|---|---|
| `bootlogo/make_boot.py` | Draws the Quantix boot animation (lightsaber + cat) → `bootanimation.zip`, `quantix_logo.png`. Needs `simba_drawn` from [simba-desktop-companion](https://github.com/000MAK/simba-desktop-companion). |
| `bootlogo/make_logo.py` | Rebuilds the MediaTek `logo` partition from *your own* backup, replacing only the splash images. The stock partition is not included here. |
| `magisk/Quantix_Bootanimation_Magisk.zip` | Boot animation as a systemless Magisk module. |
| `magisk/Quantix_Performance_Magisk.zip` | `performance` CPU governor + Doze off. MediaTek thermal/power protection is left on. |
| `debloat/` | Package lists removed with `pm uninstall -k --user 0` (reversible with `cmd package install-existing`). |
| `ROOT_PLAN.md` | The order that worked: full mtkclient backup → unlock → Magisk patch on the phone → flash. |
| `quantix_init.sh` | Termux first-run setup and banner. |

**Warning:** unlocking the bootloader wipes the phone; flashing the wrong file can brick it. Take a full backup first (see `ROOT_PLAN.md`). No warranty.

Scripts are MIT (`LICENSE`).
