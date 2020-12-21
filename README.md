# browsertime_tools
A script to facilitate importing browsertime results into a google sheet

`process_vm_ci.py {results path}` will process browsertime results in our traditional experiment structure, i.e.
```
.
└── browsertime-results
    ├── accounts.google.com
    │   ├── fenix_beta
    │   │   ├── browsertime.json
    │   │   └── pages
    │   └── fennec68
    │       ├── browsertime.json
    │       └── pages
    ├── m.facebook.com_Cristiano
    │   ├── fenix_beta
    │   │   ├── browsertime.json
    │   │   └── pages
    │   └── fennec68
    │       ├── browsertime.json
    │       └── pages
```

**Usage**
1. Process browsertime-results to a text file `$ python process_vm_ci.py browsertime-results/ > out.txt`
2. Make a copy of this google sheets tab [template](https://docs.google.com/spreadsheets/d/1ev_AgkyMBCQORMh2nBwuUcWgQNst3DxTgdeX8WJS1X4/edit#gid=1951910135&range=A12)
3. In your new tab, `File | Import | Upload` the text output `out.txt` into the [top-left blue cell](https://docs.google.com/spreadsheets/d/18qCiz3SReDgDPwhbYfuDrbnBK1030FuVWGBHWwdgCFY/edit#gid=1347397657)
<br/>Choose options `Replace data at selected cell` and `Seperator Type | Custom`, `|`
4. You can remove or add metrics by modifying `process_vm_ci.py`

