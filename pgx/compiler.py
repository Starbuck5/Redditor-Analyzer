import os
import platform
from pgx.handle_path import handle_path
from pgx.data import data


class compiler:
    # icon should be .icon for windows, .icns for mac
    # converters from normal image formats to these are easy to find through google
    @staticmethod
    def compile(name, script, icon):

        # not needed in code, just throws an error if user doesn't have pyinstaller
        import PyInstaller

        script = handle_path(script)
        scriptPath, scriptName = os.path.split(script)
        iconPath = handle_path(icon)

        if platform.system() == "Darwin":
            fileString = _get_mac(name, scriptName, scriptPath, iconPath)
        elif platform.system() == "Windows":
            fileString = _get_win(name, scriptName, scriptPath, iconPath)
        else:
            raise TypeError(
                "pgx.compiler doesn't know how to compile on this operating system"
            )

        tempFilePath = "tempCompileFile.spec"
        path = handle_path(tempFilePath)
        tempFileDir = os.path.split(path)[0]
        file = open(path, "w+")

        file.write(fileString)

        file.close()

        os.system(f"cd {tempFileDir}")
        os.system("python -m PyInstaller tempCompileFile.spec")

        os.remove(path)

        input("\nPress enter to continue")


def _get_mac(name, scriptName, scriptPath, iconPath):
    macSettings = f"""
# -*- mode: python -*-

block_cipher = None

a = Analysis(['{scriptName}'],
             pathex=['{scriptPath}'],
             binaries=[],
             datas=[],
             hiddenimports=['pkg_resources.py2_warn'],
             hookspath=['{data.get_internalpath()}'],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name="{name}",
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False)
    """
    return macSettings


def _get_win(name, scriptName, scriptPath, iconPath):
    # has to be raw string so \\'s can be preserved and continued on and such
    winSettings = r"""
# -*- mode: python -*-

block_cipher = None


a = Analysis(['{}'],
             pathex=['{}'],
             binaries=[],
             datas=[],
             hiddenimports=['pkg_resources.py2_warn'],
             hookspath=['{}'],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='{}',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False,
          icon='{}')
    """
    winSettings = winSettings.format(
        scriptName, scriptPath, data.get_internalpath(), name, iconPath
    )
    winSettings = winSettings.replace("\\", "\\\\")
    return winSettings
