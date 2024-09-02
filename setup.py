from setuptools import setup
from setuptools import find_packages
from pathlib import Path

version = "0.3.0"

install_requires = [
    "setuptools",
    "requests >= 2.22",
]

this_directory = Path(__file__).parent
long_description = (this_directory / "README.rst").read_text()

setup(
    name="certbot-dns-selectel-api-v2",
    version=version,
    description="Selectel DNS Authenticator plugin for Certbot",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://gitlab.com/alxrem/certbot-dns-selectel-api-v2",
    author="Alexey Remizov",
    author_email="alexey@remizov.org",
    license="Apache License 2.0",
    python_requires=">= 3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Plugins",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Security",
        "Topic :: System :: Installation/Setup",
        "Topic :: System :: Networking",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
    entry_points={
        "certbot.plugins": [
            "dns-selectel-api-v2 = certbot_dns_selectel_api_v2.dns_selectel_api_v2:Authenticator"
        ]
    },
)
