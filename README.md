This is a tool that 

- digests mqtt messages
- tries to detect their types
- applies some conversion to known types
- and ingests them into influx

# Install
```
python3 setup.py sdist 
pip install dist/mqtt-to-influx-0.0.1.dev10.tar.gz 
```
