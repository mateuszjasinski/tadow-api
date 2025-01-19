from setuptools import setup, find_packages

setup(
    name="tadow_api",
    version="0.0.1",
    description="Async web framework",
    packages=find_packages(),
    install_requries=[
        "uvicorn[standard]>=0.34.0",
        "pydantic>=2.10.5",
        "xmltodict>=0.14.2",
        "dicttoxml>=1.7.16",
    ],
)
