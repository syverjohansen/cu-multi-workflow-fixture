# Warehouse Jobs

Warehouse maintenance code containing a registered daily order workflow and a
separate customer cleanup routine. Both operate against a supplied DB-API
connection; the package also includes shared SQL helpers and notification
formatting.

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```
