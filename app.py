FileNotFoundError: This app has encountered an error. The original error message is redacted to prevent data leaks. Full error details have been recorded in the logs (if you're on Streamlit Cloud, click on 'Manage app' in the lower right of your app).
Traceback:
File "/home/adminuser/venv/lib/python3.12/site-packages/streamlit/runtime/scriptrunner/exec_code.py", line 88, in exec_func_with_error_handling
    result = func()
             ^^^^^^
File "/home/adminuser/venv/lib/python3.12/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 590, in code_to_exec
    exec(code, module.__dict__)
File "/mount/src/soop/app.py", line 138, in <module>
    df = load_data()
         ^^^^^^^^^^^
File "/home/adminuser/venv/lib/python3.12/site-packages/streamlit/runtime/caching/cache_utils.py", line 210, in __call__
    return self._get_or_create_cached_value(args, kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "/home/adminuser/venv/lib/python3.12/site-packages/streamlit/runtime/caching/cache_utils.py", line 235, in _get_or_create_cached_value
    return self._handle_cache_miss(cache, value_key, func_args, func_kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "/home/adminuser/venv/lib/python3.12/site-packages/streamlit/runtime/caching/cache_utils.py", line 288, in _handle_cache_miss
    computed_value = self._info.func(*func_args, **func_kwargs)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "/mount/src/soop/app.py", line 38, in load_data
    df = pd.read_excel('1804.xlsx', engine='openpyxl')  # Cargar el archivo Excel 1804.xlsx
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "/home/adminuser/venv/lib/python3.12/site-packages/pandas/io/excel/_base.py", line 495, in read_excel
    io = ExcelFile(
         ^^^^^^^^^^
File "/home/adminuser/venv/lib/python3.12/site-packages/pandas/io/excel/_base.py", line 1567, in __init__
    self._reader = self._engines[engine](
                   ^^^^^^^^^^^^^^^^^^^^^^
File "/home/adminuser/venv/lib/python3.12/site-packages/pandas/io/excel/_openpyxl.py", line 553, in __init__
    super().__init__(
File "/home/adminuser/venv/lib/python3.12/site-packages/pandas/io/excel/_base.py", line 563, in __init__
    self.handles = get_handle(
                   ^^^^^^^^^^^
File "/home/adminuser/venv/lib/python3.12/site-packages/pandas/io/common.py", line 882, in get_handle
    handle = open(handle, ioargs.mode)
             ^^^^^^^^^^^^^^^^^^^^^^^^^
