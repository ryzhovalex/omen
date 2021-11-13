from distutils.core import setup


setup(
    name="puft",
    packages=["puft"],
    version="0.2.0",
    license="MIT",
    description="Upgraded layer over Flask.",
    author = "Alexander Ryzhov",
    author_email = "thed4rkof@gmail.com",
    url = "https://github.com/ryzhovalex/puft",
    download_url = "https://github.com/ryzhovalex/puft/archive/refs/tags/0.2.0.tar.gz",
    keywords = ["flask+", "web-framework", "flask", "flask-template"],
    install_requires=[
        "flask",
        "warepy",
        "requests",
        "turbo-flask",
        "flask-migrate",
        "pytest",
    ],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",

        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",

        "License :: OSI Approved :: MIT License",

        "Programming Language :: Python :: 3.9",
    ],
)