# Tools

This project uses several tools to generate badges and an performance graph.

These tools live in the  `bin` directory and are are also configured as VScode tasks.

- [test_badge](/bin/test_badge.py)

    creates a test failed or passed badge

- [coverage_badge](/bin/coverage_badge.py)

    creates a coverage badge showing the percentage of the code tha is covered by tests

- [performance_badge](/bin/performance_badge.py)

    creates a badge showing the number of Mega Operations Per Second (Mops) for the core simulation function

- [performance_graph](/bin/performance_graph.py)

    generates a png graph showing the time taken versus the number of components to simulate


All badges are created using a [Shield.io](https://shields.io/) server running on the internal docker server.

Even though the tools are available as tasks, they also run automatically before each commit with the help of this [pre-commit script](/.git/hooks/pre-commit)

```bash
#!/bin/sh

python3 bin/coverage_badge.py coverage.json >illustrations/coverage.svg
python3 bin/test_badge.py  test.xml > illustrations/test.svg
python3 bin/performance_badge.py .benchmarks/Linux-CPython-3.12-64bit  > illustrations/performance.svg
python3 bin/performance_graph.py .benchmarks/Linux-CPython-3.12-64bit illustrations/simulation_benchmark.png
git add illustrations/coverage.svg illustrations/test.svg illustrations/performance.svg illustrations/simulation_benchmark.png
```