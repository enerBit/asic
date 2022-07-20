import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="asic",
    version="0.0.1",
    author="enerBit",
    author_email="jtamayoh@gmail.com",
    description="Download ASIC files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/enerBit/asic.git",
    include_package_data=True,
    # packages=['xmasic'],
    packages=setuptools.find_packages("src"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    package_dir={"": "src"},
    package_data={"": ["data/"]},
    install_requires=[
        "requests",
        "html5lib",
        "BeautifulSoup4",
        "pytz",
        "pandas",
        "pydantic",
        "typer[all]",
    ],
    entry_points={
        "console_scripts": ["asic = asic.cli:cli"],
    },
)
