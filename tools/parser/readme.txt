Input: base64 initialinfo data in b64.txt
Output: Starting `player.db`, accumulative `manifest.db`, starting `diff_manifest.db`, json files in `config` folder

A `diff_manifest.db` will be generated with the same schema of the manifest db, with the addition of a delete column.

If you wish a row from the official server to not be added, add a row there, and set pk appropriately and delete to 1.

If you wish to override the official server content, add a row there, and set pk and field value appropriately. Set field to string "None" for python to apply it as actual null.