from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="super-agents",
    version="2.0.0",
    author="AICODE Labs",
    author_email="info@aicode-labs.com",
    description="AICODE Labs - AI-native software development company composed of autonomous agents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Nom-nom-hub/super-agents",
    packages=find_packages(where="company"),
    package_data={
        'company': ['agent_registry.yaml', 'agents/*.yaml', 'agents/*.md', 'scripts/*.sh', 'scripts/*.ps1'],
    },
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'aicode=company.cli:cli',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires='>=3.8',
)