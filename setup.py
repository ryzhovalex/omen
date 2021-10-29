from distutils.core import setup


setup(
    name="omen",
    packages=["omen"],
    version="v0.1.1-proto",
    license="MIT",
    description="Upgraded layer over Flask.",
    author = "Alexander Ryzhov",
    author_email = "thed4rkof@gmail.com",
    url = "https://github.com/ryzhovalex/omen",
    download_url = "https://github.com/ryzhovalex/omen/archive/refs/tags/0.1.0-proto.tar.gz",
    keywords = ["flask+", "web-framework", "flask", "flask-template"],
    install_requires=[
        "flask",
        "requests",
        "turbo-flask",
        "flask-migrate",
        "loguru",
        "pytest",
    ],
    classifiers=[
        "Development Status :: 1 - Planning",

        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",

        "License :: OSI Approved :: MIT License",

        "Programming Language :: Python :: 3.9",
    ],
)