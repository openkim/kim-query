import setuptools
import versioneer

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="kim-query",
    version=versioneer.get_version(),
    description=(
        "Helper routines for querying the OpenKIM Repository"
    ),
    author="Daniel S. Karls",
    author_email="karl0100@umn.edu",
    url="https://github.com/openkim/kim-query",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    license="CDDL",
    install_requires=["requests"],
    python_requires='>=3.6',
    keywords=['kim-query', 'kim_query', 'openkim'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        "License :: OSI Approved :: Common Development and Distribution License 1.0 (CDDL-1.0)",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
        'Intended Audience :: Science/Research',
    ],
    cmdclass=versioneer.get_cmdclass()
)
