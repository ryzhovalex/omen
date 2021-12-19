import pathlib
from setuptools import setup, find_packages


here = pathlib.Path(__file__).parent.resolve()


setup(
    name="puft",
    version="0.3.0.dev10",
    packages=find_packages(),
    include_package_data=True,
    license="MIT",
    description="Upgraded layer over Flask.",
    author="Alexander Ryzhov",
    author_email="thed4rkof@gmail.com",
    url="https://github.com/ryzhovalex/puft",
    keywords=["flask+", "web-framework", "flask", "flask-template"],
    entry_points={
        "console_scripts": [
            "puft = puft.helpers.cli:main",
        ],
    },
    install_requires=[
        "flask",
        "warepy",
        "requests",
        "turbo-flask",
        "flask-migrate",
        "pytest",
        "flask-cors",
        "flask-session"
    ],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",

        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",

        "License :: OSI Approved :: MIT License",

        "Programming Language :: Python :: 3.9",
    ],
)
