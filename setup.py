import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="PyBroeModules",
    version="1.0.0",
    author="Martin Brösamle",
    author_email="m@martinbroesamle.de",
    description="Python Modules I, personnally, use regualarly; feel free :-)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/broesamle/PyBroeModules",
    packages=setuptools.find_packages(),
    keywords=[],
    python_requires='>=3.7')
