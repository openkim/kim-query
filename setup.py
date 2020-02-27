import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="kim-query",
    version="1.0.0",
    description=(
        "Helper routines for querying the OpenKIM Repository"
    ),
    author=["Daniel S. Karls"],
    url="https://github.com/openkim/kim-python-utils",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    license="CDDL",
    install_requires=["requests"],
    python_requires='>=2.7',
    keywords='kim_query',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        "License :: OSI Approved :: Common Development and Distribution License 1.0 (CDDL-1.0)",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
        'Intended Audience :: Science/Research',
    ],
)
