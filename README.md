# browsertime_tools
Scripts I'm using for browsertime for android

## Workflow:


• Configure the following in `test_cold_load_desktop.py`
```
    firefox binary path
    iterations
    test_configs (a tuple of (experiment name, firefox preferences)
```

• Run this script to generate results `$ python ./test_cold_load_desktop.py`

• Process the results to standard out with `$python ./process_process_loadTime.py`
