from setuptools import setup, find_packages

setup(
    name="soc-automation-framework",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "selenium>=4.0.0",
        "webdriver-manager>=4.0.0",
        "pyyaml>=6.0.0",
    ],
    python_requires=">=3.8",
    author="SEU_NOME",
    description="Framework de automação para Sistema SOC com Selenium",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/seu-usuario/soc-automation-framework",
)