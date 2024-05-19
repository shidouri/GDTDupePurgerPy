# dupe_fixer.py 
# by Shidouri [shid]
# Used to purge duplicate assets from source GDTs for the Black Ops III Mod Tools.

import os
import re
import sys
import shutil
import requests
import datetime
from pathlib import Path


class GDT_Asset:
    def __init__(self, assetname, assettype, gdtpath, gdtrelpath, gdtname):
        self.asset = assetname
        self.type = assettype
        self.gdtpath = gdtpath
        self.gdtrelpath = gdtrelpath
        self.gdtname = gdtname


class DupeFlags:
    def __init__(self, should_print=True, should_bak=True):
        self.should_print = should_print
        self.should_bak = should_bak


class GDTDP:
    def _get_dupe_fixer_flags_from_args(self, args) -> DupeFlags:
        flags = DupeFlags()
        if len(args) < 2:
            return flags
        
        for arg in args:
            arg = arg.replace('+', '').replace('-', '').replace('/', '')
            if arg in {'no_print', 'no_log', 'noshow', 'quiet', 'shh'}:
                flags.should_print = False
            elif arg in {'developer_no_backup_use_wisely', 'nobak'}:
                flags.should_bak = False

        return flags

    def _read_gdtdef_or_retrieve(self, outfile_name, req_url) -> list[str]:
        try:
            with open(outfile_name, 'r') as stock_gdts:
                return [entry.strip() for entry in stock_gdts.readlines()]
        except FileNotFoundError:
            print(f'{outfile_name} not found.')
            print(f'Downloading gdtdef from GitHub ({req_url})')
            response = requests.get(req_url)
    
            if response.status_code == requests.codes.ok:
                with open(outfile_name, 'w') as stock_gdt:
                    stock_gdt.write(response.text)
                return response.text.splitlines()
            else:
                raise Exception(f"Error: Could not retrieve {outfile_name} from {req_url} (status code {response.status_code})")

    def _get_midgetblaster_gdts(self) -> list[str]:
        return self._read_gdtdef_or_retrieve('midget.gdtdef', 'https://raw.githubusercontent.com/shidouri/GDTDupePurgerPy/main/midget.gdtdef')

    def _get_stock_gdts(self) -> list[str]:
        return self._read_gdtdef_or_retrieve('stock.gdtdef', 'https://raw.githubusercontent.com/shidouri/GDTDupePurgerPy/main/stock.gdtdef')

    def split_dupe_error_line_to_object(self, rex_pattern, error_line) -> GDT_Asset | None:
        match = re.findall(rex_pattern, error_line)
        if not match or len(match[0]) < 4:
            return None
        
        xtype, xasset, gdtpath, gdtline = match[0]
        gdtpath = f"{gdtpath}.gdt".replace('\\', '/').strip()
        gdtname = gdtpath.split('/')[-1]
        gdtrelpath = gdtpath.split('call of duty black ops iii/')[-1]
        
        return GDT_Asset(xasset, xtype, gdtpath, gdtrelpath, gdtname)

    def _read_dupe_error_file(self, dupe_error_txt_file_path) -> list[GDT_Asset]:
        rex_pattern = r"ERROR: Duplicate '(.+?)' asset '(.+?)' found in (.+?)\.gdt:(.+?)\n"
        dupe_error_objects = []

        if not os.path.exists(dupe_error_txt_file_path):
            with open(dupe_error_txt_file_path, 'x'):
                pass
            print("dupe_error.txt was not found.\nIt has now been created for you.")
            return dupe_error_objects

        with open(dupe_error_txt_file_path, 'r') as dupe_error_txt_file:
            for dupe_line in dupe_error_txt_file:
                obj = self.split_dupe_error_line_to_object(rex_pattern, dupe_line)
                if obj:
                    dupe_error_objects.append(obj)
        
        return dupe_error_objects

    def _purge_asset_from_gdt_lines(self, asset, lines, out_path):
        purging_lines = False
        return_lines = []

        for i, line in enumerate(lines):
            if line == "\t{\n" and asset in lines[i - 1] and not purging_lines:
                purging_lines = True
                return_lines.pop()  # Remove the asset line
            elif line == "\t}\n" and purging_lines:
                purging_lines = False
            elif not purging_lines:
                return_lines.append(line)
                
        if self.dupe_fixer_flags.should_print: print(f"Purging {asset} from {out_path}...")
        Path(out_path).write_text(''.join(return_lines))
        open('./dupe_error.txt', 'w').close()

    def _backup_old_gdt(self, name, gdt) -> None:
        timestamp = datetime.datetime.now().isoformat().replace(':', '_')
        backup_path = Path('./backup')
        backup_path.mkdir(exist_ok=True)

        backup_file = backup_path / f"{timestamp}_{name}"
        shutil.copy2(gdt, backup_file)

    def _remove_dupe_from_gdt(self, asset, gdt_name, gdt_path) -> None:
        if self.dupe_fixer_flags.should_bak and gdt_name not in self.already_backed_up: 
            self._backup_old_gdt(gdt_name, gdt_path)
            self.already_backed_up.append(gdt_name)

        with open(gdt_path, 'r') as old_gdt:
            old_lines = old_gdt.readlines()

        self._purge_asset_from_gdt_lines(asset, old_lines, gdt_path)

    def _is_midget_gdt(self, gdt_rel_path) -> bool:
        return gdt_rel_path in self.stock_midgetblaster_gdts

    def _is_stock_gdt(self, gdt_rel_path) -> bool:
        return gdt_rel_path in self.stock_gdts

    def __init__(self, error_log='./dupe_error.txt', dupe_fixer_flags = None):
        self.dupe_fixer_flags = self._get_dupe_fixer_flags_from_args(dupe_fixer_flags or sys.argv)

        self.stock_gdts = self._get_stock_gdts()
        if not self.stock_gdts:
            input("stock.gdtdef could not be retrieved.\n")
            sys.exit(0)

        self.stock_midgetblaster_gdts = self._get_midgetblaster_gdts()
        if not self.stock_midgetblaster_gdts:
            input("midget.gdtdef could not be retrieved.\n")
            sys.exit(0)

        self.dupe_object_list = self._read_dupe_error_file(error_log)
        if not self.dupe_object_list:
            input("No GDTs to edit.\n")
            sys.exit(0)

        self.dupes_to_purge = []
        self.already_backed_up = []
        self.dupe_assets_to_purge = []

        for dupe_error_object in self.dupe_object_list:
            if self._is_midget_gdt(dupe_error_object.gdtrelpath):
                continue
            if self._is_stock_gdt(dupe_error_object.gdtrelpath):
                error_gdt_name = dupe_error_object.gdtname
                for inner_object in self.dupe_object_list:
                    if inner_object.gdtname == error_gdt_name:
                        continue
                    if inner_object.gdtname != error_gdt_name and self._is_midget_gdt(inner_object.gdtrelpath) and dupe_error_object.asset not in self.dupe_assets_to_purge:
                        self.dupes_to_purge.append(dupe_error_object)
                        self.dupe_assets_to_purge.append(dupe_error_object.asset)
                        break
            else:
                if dupe_error_object.asset not in self.dupe_assets_to_purge:
                    self.dupes_to_purge.append(dupe_error_object)
                    self.dupe_assets_to_purge.append(dupe_error_object.asset)

        for entry in self.dupes_to_purge:
            self._remove_dupe_from_gdt(entry.asset, entry.gdtname, entry.gdtpath)


if __name__ == "__main__":      GDTDP()
